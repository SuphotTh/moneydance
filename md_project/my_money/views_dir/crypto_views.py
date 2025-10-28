from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from ..models import CryptoPurchase
from datetime import datetime, date, timedelta
from django.db import transaction
from django.conf import settings
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from decimal import Decimal
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import csv
import re
import io
import json
import time
import hmac
import hashlib
import requests
import pandas as pd
import matplotlib.pyplot as plt
import base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Can also use DEBUG

api_key = settings.BITKUB_API
api_secret = settings.BITKUB_SECRET_KEY

binance_api = settings.BINANCE_API
binance_secret_key = settings.BINANCE_SECRET_KEY

@login_required
def wallet_balances(request):
    table_data, total_value = get_bitkub_wallet()
    exchange2, table_data2, total_value2 = get_binance_wallet()
    logger.info("TABLE DATA: %s", table_data)
    logger.info("TOTAL VALUE: %s", total_value)
    logger.info("TABLE DATA2: %s", table_data2)
    logger.info("TOTAL VALUE2: %s", total_value2)

    return render(request, 'crypto.html', {
        'exchange': "bitkub",
        'data': table_data,
        'total_value': total_value,
        'exchange2': exchange2,
        'data2': table_data2,
        'total_value2': total_value2,
         })

@login_required
def place_order(request):
    if request.method == 'POST':
        sym = request.POST.get('sym')
        sym = (sym + '_thb').lower()
        amt = request.POST.get('amt')

        if not sym or not amt:
            return JsonResponse({'error': 'Missing sym or amt'}, status=400)

        try:
            amt = int(float(amt))
        except ValueError:
            return JsonResponse({'error': 'Invalid amount'}, status=400)

        fear_greed, classification = get_fear_greed_index()
        amt = ((100-int(fear_greed))*0.01)* amt #calculate amount of purchase 

        # Call the same trigger function used by n8n
        return trigger(request, sym, amt, fear_greed, classification)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_fear_greed_index():
    #GET FearAndGreed Index
    url = "https://api.alternative.me/fng/" #get Fear&Greet Index
    params = {
        "limit": 1,        # latest value only
        "format": "json"   # json format
    }
    response = requests.get(url, params=params)
    data = response.json()
    fear_greed = data["data"][0]["value"]
    classification = data["data"][0]["value_classification"]
    return fear_greed, classification

@csrf_exempt
def n8n_trigger(request):
    api_key2 = request.headers.get('Authorization')
    if api_key2 != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)
    
    fear_greed, classification = get_fear_greed_index()

    sym = request.headers.get('Symbol')
    amt = int(request.headers.get('Amount'))
    amt = ((100-int(fear_greed))*0.01)* amt #calculate amount of purchase 

    logger.info("Symbol: %s", sym)
    logger.info("Amount: %s", amt)
    return trigger(request, sym, amt, fear_greed, classification)
    # return JsonResponse({'sym': sym,
    #                     'amt': amt,
    #                     'fear_greed': fear_greed,
    #                     'classification': classification})

def trigger(request, sym, amt, fear_greed, classification):
    # --- Identify caller type ---
    api_key2 = request.headers.get('Authorization', '')
    if api_key2.startswith('Bearer '):
        caller_type = 'n8n'
    elif request.headers.get('X-CSRFToken'):
        caller_type = 'frontend'
    else:
        caller_type = 'unknown'

    logger.info("Caller type detected: %s", caller_type)

    # --- Security: allow only known sources ---
    if caller_type == 'n8n':
        if api_key2 != f'Bearer {settings.APIKEY}':
            return JsonResponse({'error': 'Unauthorized Access'}, status=401)
    elif caller_type == 'frontend':
        # Optionally require login for frontend
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=403)
    else:
        return JsonResponse({'error': 'Unauthorized source'}, status=401)

    # --- Proceed with trading logic ---
    pre_balances, pre_table_value = get_bitkub_wallet()

    # Try to load request data (safe for both)
    try:
        data = json.loads(request.body)
        logger.info("Received data: %s", data)
    except Exception:
        data = {}

    timestamp = str(int(time.time() * 1000))
    method = 'POST'
    request_path = '/api/v3/market/place-bid'

    order_data = {
        'sym': sym,
        'amt': amt,
        'rat': 0,
        'typ': 'market'
    }

    body = json.dumps(order_data, separators=(',', ':'))
    payload = timestamp + method + request_path + body
    signature = hmac.new(
        api_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': api_key,
        'X-BTK-TIMESTAMP': timestamp,
        'X-BTK-SIGN': signature
    }

    url = 'https://api.bitkub.com' + request_path
    response = requests.post(url, headers=headers, data=body)

    try:
        confirmed = response.json()
    except Exception as e:
        logger.error("Error parsing Bitkub response: %s", e)
        confirmed = {'error': 'Invalid JSON'}

    logger.info("CONFIRMED : %s", confirmed)

    time.sleep(1)  # small delay before post-balance update
    post_balances, post_table_value = get_bitkub_wallet()

    pre_df = pd.DataFrame(pre_balances)
    post_df = pd.DataFrame(post_balances)

    logger.info("PRE_BALANCES : %s", pre_df.to_string(index=False))
    logger.info("POST_BALANCES : %s", post_df.to_string(index=False))

    database_update(pre_balances, post_balances, confirmed, order_data, fear_greed, classification)

    return JsonResponse({'status': confirmed, 
                        'source': caller_type,
                        'sym': sym,
                        'amt': amt,
                        'fear_greed': fear_greed,
                        'classification': classification})

@login_required
def purchased_report_page(request):
    # Get symbols from database as list
    db_symbols = list(CryptoPurchase.objects.values_list('sym', flat=True).distinct())

    # Extra symbols to always include
    extra_symbols = ['USDT', 'BNB', 'XRP']

    # Merge lists and remove duplicates while preserving order
    seen = set()
    symbols = []
    for s in db_symbols + extra_symbols:
        if s not in seen:
            seen.add(s)
            symbols.append(s)

    context = {
        'symbols': symbols,
        'sym': 'BTC',  # default symbol
    }
    return render(request, 'purchased_report.html', context)    

@login_required
def purchased_report(request):
    sym = request.GET.get('sym', 'BTC')  # default BTC
    page = int(request.GET.get('page', 1))
    
    purchases = CryptoPurchase.objects.filter(sym=sym).order_by('-date', '-time')
    paginator = Paginator(purchases, 8)
    page_obj = paginator.get_page(page)

    last_record = CryptoPurchase.objects.order_by('-date', '-time').first()
    # acc_post_bal = last_record.acc_post_bal if last_record else None
    
    # Latest market price
    table_data, total_value = get_bitkub_wallet()
    # Latest market price
    acc_last_price = Decimal('0')
    for d in table_data:
        if d['symbol'] == sym:
            acc_last_price = Decimal(str(d['last']))  # convert float to Decimal
            acc_total_qty = Decimal(str(d['qty']))  # get total qty of crypto in account
            acc_total_value = Decimal(str(d['value'])) # get Total value from srypto account
            break

    acc_post_bal = next((item['qty'] for item in table_data if item['symbol'] == 'THB'), 0)
    # Calculate
    dca_cost = sum(p.purchase_amount for p in purchases)
    dca_qty = sum(p.purchase_qty for p in purchases)
    market_value = dca_qty * acc_last_price
    p_and_l = market_value - dca_cost
    percent = p_and_l/dca_cost * 100

    usd_price = get_coinmarketcap_data(sym)
    # get coin price in USD
    # logger.info("USD = %s", usd_price)

    data = {
        'page_obj': [
            {
                'id': p.id,
                'date': p.date.strftime('%Y-%m-%d'),
                'time': p.time.strftime('%H:%M:%S'),
                'sym': p.sym,
                'crypto_post_bal': float(p.crypto_post_bal or 0),
                'classification': p.classification or "",
                'fear_greed': p.fear_greed or 0,
                'purchase_amount': float(p.purchase_amount),
                'purchase_qty': format(p.purchase_qty, '.8f'),
                'purchase_price': float(p.purchase_price),
            } for p in page_obj
        ],
        'pagination': {
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
        },
        'acc_post_bal': acc_post_bal,
        'acc_total_qty': acc_total_qty,
        'acc_total_value': acc_total_value,
        'acc_last_price': acc_last_price,
        'dca_qty': dca_qty,
        'dca_value': market_value,
        'dca_cost': float(dca_cost),
        'p_and_l': float(p_and_l),
        'percent': float(percent),
        'usd_price': usd_price,
    }
    # logger.info("total_cost : ", total_cost)
    # logger.info("total_cost : ", dca_cost)
    return JsonResponse(data)

def get_bitkub_wallet():
    # Configuration
    timestamp = str(int(time.time() * 1000))
    method = 'POST'
    request_path = '/api/v3/market/wallet'
    body = ''  # Empty string for POST body

    # Generate signature
    payload = timestamp + method + request_path + body
    signature = hmac.new(
        api_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Make request
    url = 'https://api.bitkub.com' + request_path
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': api_key,
        'X-BTK-TIMESTAMP': timestamp,
        'X-BTK-SIGN': signature
    }

    wallet_response = requests.post(url, headers=headers, data=body)
    wallet = wallet_response.json()

    # /api/v3/market/ticker
    timestamp = str(int(time.time() * 1000))
    method = 'GET'
    request_path = '/api/v3/market/ticker'
    body = ''  # Empty string for POST body

    # Generate signature
    payload = timestamp + method + request_path + body
    signature = hmac.new(
        api_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Make request
    url = 'https://api.bitkub.com' + request_path
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': api_key,
        'X-BTK-TIMESTAMP': timestamp,
        'X-BTK-SIGN': signature
    }
    response = requests.get(url, headers=headers, data=body)
    ticker = response.json()
    # print(ticker)

    ticker_prices = {
        item['symbol'].replace('_THB', ''): float(item['last'])
        for item in ticker
    }
    ticker_prices['THB'] = 1

    # Build the final table
    table_data = []
    for symbol, qty in wallet['result'].items():
        if symbol in ticker_prices:
            last_price = ticker_prices[symbol]
            value = qty * last_price
            if value > 0:  # ✅ กรองเฉพาะรายการที่มีมูลค่า
                table_data.append({
                    'symbol': symbol,
                    'qty': qty,
                    'last': last_price,
                    'value': round(value, 2)
                })
    total_value = sum(item['value'] for item in table_data)

    return table_data, total_value

def get_binance_wallet():
    # === 1. Get account balances ===
    base_url = "https://api.binance.th/api/v1/accountV2"
    timestamp = int(time.time() * 1000)
    params = {'timestamp': timestamp}

    # Generate signature
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(binance_secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature

    headers = {
        'Accept': 'application/json',
        'X-MBX-APIKEY': binance_api
    }

    # Request account balances
    r = requests.get(base_url, params=params, headers=headers)
    account_data = r.json()

    balances = account_data.get('balances', [])
    table_data2 = []
    total_value2 = 0.0

    # === 2. For each asset, get last price and compute value ===
    for bal in balances:
        symbol = bal.get('asset')
        qty = float(bal.get('free', 0))

        # Skip if quantity is zero or the asset is THB
        if qty == 0:
            continue

        if symbol == 'THB':
            last_price = 1.0
            value = qty
        else:
            # Construct pair (e.g. BTC → BTCTHB)
            market_symbol = f"{symbol}THB"

            ticker_url = "https://api.binance.th/api/v1/ticker/24hr"
            r_ticker = requests.get(ticker_url, params={'symbol': market_symbol}, headers={'Accept': 'application/json'})
            ticker_data = r_ticker.json()

            # Extract last price (if not found, assume 0)
            last_price = float(ticker_data.get('lastPrice', 0))
            value = qty * last_price

        table_data2.append({
            'symbol': symbol,
            'qty': round(qty, 8),
            'last': round(last_price, 2),
            'value': round(value, 2)
        })

        total_value2 += value

    # === 3. Sort table and format total ===

    host = base_url.split("//")[1].split("/")[0]   # "api.binance.th"
    exchange2 = host.split(".")[1]                      # "binance"
    table_data2 = sorted(table_data2, key=lambda x: x['symbol'])
    total_value2 = round(total_value2, 2)
    logger.info("TABLE DATA2: %s", table_data2)
    logger.info("TOTAL VALUE2: %s", total_value2)
    return exchange2, table_data2, total_value2


def get_coinmarketcap_data(sym):
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': sym,
        'convert': 'USD',
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '9a7aa593-ddda-46e5-84e5-579e2b03721e',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = response.json()  # already converts to dict

        # Use sym as key
        coin_data = data['data'][sym][0]['quote']['USD']
        price = coin_data['price']
        percent_24h = coin_data['percent_change_24h']

        usd_price = f"${price:,.2f} (24h: {percent_24h:.2f}%)"
        return usd_price

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return f"Error: {e}"
    except KeyError:
        return f"Error: Coin symbol '{sym}' not found."

def database_update(pre_balances, post_balances, confirmed, order_data, fear_greed, classification):
    # Only proceed if the order was successful
    if confirmed.get('error') != 0:
        return  # Do nothing if there's an error

    # Extract the symbol from order_data
    sym = order_data['sym'].replace('_thb', '').upper()

    # Transaction ID
    transaction = confirmed['result']['id']

    # Current date and time
    now = datetime.now()
    date_str = now.date()  # yyyy-mm-dd
    time_str = now.time()  # hh:mm:ss

    # Helper functions
    def find_qty(balances, symbol):
        for item in balances:
            if item['symbol'] == symbol:
                return float(item['qty'])
        return 0.0

    def find_last(balances, symbol):
        for item in balances:
            if item['symbol'] == symbol:
                return float(item['last'])
        return 0.0

    # Account balances
    acc_pre_bal = find_qty(pre_balances, 'THB')
    acc_post_bal = find_qty(post_balances, 'THB')

    # Crypto balances
    crypto_pre_bal = find_qty(pre_balances, sym)
    crypto_post_bal = find_qty(post_balances, sym)

    # Purchase amount in fiat
    purchase_amount = confirmed['result']['amt']

    # Purchase price = average of last prices pre & post
    if (find_last(pre_balances, sym) > 0) and (find_last(post_balances, sym) > 0):
        purchase_price = (find_last(pre_balances, sym) + find_last(post_balances, sym)) / 2
    else:
        purchase_price = find_last(post_balances, sym)



    # Purchase quantity = difference in crypto balances
    purchase_qty = crypto_post_bal - crypto_pre_bal

    # Save to DB
    CryptoPurchase.objects.create(
        sym=sym,
        transaction=transaction,
        date=date_str,
        time=time_str,
        acc_pre_bal=acc_pre_bal,
        acc_post_bal=acc_post_bal,
        crypto_pre_bal=crypto_pre_bal,
        crypto_post_bal=crypto_post_bal,
        purchase_amount=purchase_amount,
        purchase_qty=purchase_qty,
        purchase_price=purchase_price,
        fear_greed=fear_greed,
        classification=classification,

    )



@login_required
def deposit_history(request):
    """Render the deposit history page"""
    return render(request, 'deposit_history.html')

@login_required
def deposit_history_bitkub(request):
    """Fetch deposit history from Bitkub API"""
    timestamp = str(int(time.time() * 1000))
    method = 'POST'
    request_path = '/api/v3/fiat/deposit-history'

    # Get pagination parameters from request
    page = request.GET.get('p', 1)
    limit = request.GET.get('lmt', 10)
    
    param = {'p': int(page), 'lmt': int(limit)}
    body = json.dumps(param, separators=(',', ':'))

    # Create signature
    payload = timestamp + method + request_path + body
    signature = hmac.new(
        api_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # API request
    url = 'https://api.bitkub.com' + request_path
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': api_key,
        'X-BTK-TIMESTAMP': timestamp,
        'X-BTK-SIGN': signature
    }

    try:
        response = requests.post(url, headers=headers, data=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "error": 1,
            "message": f"API request failed: {str(e)}",
            "result": []
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "error": 1,
            "message": str(e),
            "result": []
        }, status=500)

@login_required
def deposit_history_binanceth(request):
    base_url = "https://api.binance.th/api/v1/capital/deposit/history"

    timestamp = int(time.time() * 1000)
    params = {
        'startTime': timestamp - 30*24*60*60*1000,  # 30 days ago
        'endTime': timestamp,
        'limit': 10,
        'timestamp': timestamp
    }
    # Create query string
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])

    # Generate signature (HMAC SHA256)
    signature = hmac.new(binance_secret_key.encode('utf-8'),
                        query_string.encode('utf-8'),
                        hashlib.sha256).hexdigest()

    # Add signature to params
    params['signature'] = signature

    # Add headers
    headers = {
        'Accept': 'application/json',
        'X-MBX-APIKEY': binance_api
    }

    # ✅ Use GET request
    try:
        r = requests.get(base_url, params=params, headers=headers)
        data = r.json() if r.ok else {"error": r.text}
        return JsonResponse({
            "status_code": r.status_code,
            "result": data
        }, safe=False)

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status_code": 500,
            "error": str(e)
        }, safe=False)

#def custom_404(request, exception):
#     return HttpResponseNotFound("404 Page Not Found")

# def custom_500(request):
#     return HttpResponseServerError("500 Internal Server Error")