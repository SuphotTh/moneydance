from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..models import CryptoPurchase
from datetime import datetime, date, timedelta
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from decimal import Decimal
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from typing import Optional, Dict, Any
import csv
import re
import io
import json
import pandas as pd
import matplotlib.pyplot as plt
import base64
import hmac, hashlib, time, requests, logging


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

@login_required
def crypto_signal_list(request):
    # --- Get Bitkub wallet ---
    table_data, total_value = get_bitkub_wallet()
    symbols =[]
    # --- Extract symbols ---
    raw_symbols = [row['symbol'] for row in table_data]
    for s in raw_symbols:
        if s == "THB":  
            continue  # skip THB (no Binance data)
        if s == "KUB":  
            continue  # skip THB (no Binance data)
        if s == "USDT":
            continue  # skip USDT (stablecoin)
        symbols.append(s + "USDT")
    # --- Collect results here ---
    
    signal_list = []

    # --- Loop symbols and get EMA signals ---
    for symbol in symbols:
        latest_signals = get_latest_signals(symbol)

        if latest_signals["Symbol"].endswith("USDT"):
            latest_signals["Symbol"] = latest_signals["Symbol"][:-4]

        signal_list.append(latest_signals)

    # --- Return to frontend ---
    return render(request, "crypto_signal_list.html", {
        "signal_list": signal_list,
    })

def get_latest_signals(symbol):
    # --- Parameters ---
    interval = "1d"
    limit = 500
    ema_fast_period = 12
    ema_slow_period = 26

    # --- Fetch Binance data ---
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()

    # --- Convert to DataFrame ---
    columns = [
        "Open time", "Open", "High", "Low", "Close", "Volume",
        "Close time", "Quote asset volume", "Number of trades",
        "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
    ]
    df = pd.DataFrame(data, columns=columns)
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    df["Open time"] = pd.to_datetime(df["Open time"], unit="ms")

    # --- Calculate EMAs ---
    df["EMA_fast"] = df["Close"].ewm(span=ema_fast_period, adjust=False).mean()
    df["EMA_slow"] = df["Close"].ewm(span=ema_slow_period, adjust=False).mean()

    # --- Define Zones ---
    df["Zone"] = "Neutral"
    df.loc[(df["EMA_fast"] > df["EMA_slow"]) & (df["Close"] > df["EMA_fast"]), "Zone"] = "Green"
    df.loc[(df["EMA_fast"] < df["EMA_slow"]) & (df["Close"] > df["EMA_fast"]) & (df["Close"] > df["EMA_slow"]), "Zone"] = "Blue"
    df.loc[(df["EMA_fast"] < df["EMA_slow"]) & (df["Close"] > df["EMA_fast"]) & (df["Close"] < df["EMA_slow"]), "Zone"] = "LightBlue"
    df.loc[(df["EMA_fast"] < df["EMA_slow"]) & (df["Close"] < df["EMA_fast"]), "Zone"] = "Red"
    df.loc[(df["EMA_fast"] > df["EMA_slow"]) & (df["Close"] < df["EMA_fast"]) & (df["Close"] < df["EMA_slow"]), "Zone"] = "Orange"
    df.loc[(df["EMA_fast"] > df["EMA_slow"]) & (df["Close"] < df["EMA_fast"]) & (df["Close"] > df["EMA_slow"]), "Zone"] = "Yellow"

    # --- Detect EMA crossover buy/sell ---
    df["Buy"] = (df["EMA_fast"] > df["EMA_slow"]) & (df["EMA_fast"].shift(1) <= df["EMA_slow"].shift(1))
    df["Sell"] = (df["EMA_fast"] < df["EMA_slow"]) & (df["EMA_fast"].shift(1) >= df["EMA_slow"].shift(1))

    # --- Prepare latest signals ---
    latest = df.tail(1)[["Open time", "Close", "EMA_fast", "EMA_slow", "Zone", "Buy", "Sell"]]
    latest.insert(0, 'Symbol', symbol)
    latest.rename(columns={"Open time": "Open_time"}, inplace=True)
    latest_signals = latest.to_dict(orient="records")[0]
    return latest_signals

@csrf_exempt
def n8n_trigger(request):
    api_key2 = request.headers.get('Authorization')
    if api_key2 != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)
    
    sym = request.headers.get('Symbol')
    amt = int(request.headers.get('Amount'))

    fear_greed, classification = get_fear_greed_index()
    # zone = get_latest_signals(sym)

    amt = ((100-int(fear_greed))*0.01)* amt #calculate amount of purchase 

    logger.info("Symbol: %s", sym)
    logger.info("Amount: %s", amt)
    return trigger(request, sym, amt, fear_greed, classification)

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
    
    # purchases = CryptoPurchase.objects.filter(sym=sym).order_by('-date', '-time')
    purchases = CryptoPurchase.objects.filter(sym=sym).order_by('-transaction')
    paginator = Paginator(purchases, 8)
    page_obj = paginator.get_page(page)

    last_record = CryptoPurchase.objects.order_by('-date', '-time').first()
    # acc_post_bal = last_record.acc_post_bal if last_record else None
    
    # Latest market price
    table_data, total_value = get_bitkub_wallet()
    # Latest market price
    acc_last_price = Decimal('0')
    acc_total_value = Decimal('0')
    acc_total_qty = Decimal('0')
    for d in table_data:
        if d['symbol'] == sym:
            acc_last_price = Decimal(str(d.get('last', 0)))      # handle missing key
            acc_total_qty = Decimal(str(d.get('qty', 0)))        # handle missing or null value
            acc_total_value = Decimal(str(d.get('value', 0)))    # handle missing or null value
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
                'order_id': p.transaction,
                'date': p.date.strftime('%Y-%m-%d'),
                'time': p.time.strftime('%H:%M:%S'),
                'sym': p.sym,
                'side': p.spare_char1,
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

    # *****************************************************
    # time.sleep(1)  # small delay before post-balance update
    post_balances, post_table_value = get_bitkub_wallet()

    database_update(post_balances, confirmed, order_data, fear_greed, classification)
    #********************************************************

    return JsonResponse({'status': confirmed, 
                        'source': caller_type,
                        'sym': sym,
                        'amt': amt,
                        'fear_greed': fear_greed,
                        'classification': classification})

def database_update(post_balances, confirmed, order_data, fear_greed, classification):
    # Only proceed if the order was successful
    if confirmed.get('error') != 0:
        return  # Do nothing if there's an error

    # Extract the symbol from order_data
    sym = order_data['sym'].replace('_thb', '').upper()
    symbol_thb = order_data['sym'].upper()

    # Transaction ID
    transaction = confirmed['result']['id']
    purchased_transactions = get_purchased_transactions(symbol_thb, 5) 
    match = next(
        (item for item in purchased_transactions["result"] if item["order_id"] == transaction),
        None
    )
    if match:
        side = match["side"]
        purchase_price = float(match["rate"])
        fee = float(match["fee"])
        purchase_amount = float(match["amount"])
        timestamp = match["ts"]  # keep as integer or convert to datetime if needed
    else:
        logger.info("TRANSACTION NOT FOUND !")

    # Current date and time
    dt = datetime.fromtimestamp(timestamp / 1000)
    # Extract date and time strings
    date_str = dt.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H:%M:%S")

    if side == "buy":
        purchase_amount = purchase_amount - fee
        purchase_qty = purchase_amount/purchase_price
    elif side == "sell":
        purchase_amount = ((purchase_price * purchase_amount) - fee) * -1
        purchase_qty = purchase_amount * -1

    logger.info (f"SIDE : %s", side)

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
    acc_post_bal = find_qty(post_balances, 'THB')
    # Crypto balances
    crypto_post_bal = find_qty(post_balances, sym)

    # Save to DB
    CryptoPurchase.objects.create(
        sym=sym,
        transaction=transaction,
        date=date_str,
        time=time_str,
        acc_pre_bal=0,
        crypto_pre_bal=0,
        acc_post_bal=acc_post_bal,
        crypto_post_bal=crypto_post_bal,
        purchase_amount=purchase_amount,
        purchase_qty=purchase_qty,
        purchase_price=purchase_price,
        fear_greed=fear_greed,
        classification=classification,
        spare_char1=side,
    )

def get_purchased_transactions(symbol, limit):
    API_KEY = api_key
    API_SECRET = api_secret
    BASE_URL = "https://api.bitkub.com"

    def generate_signature(timestamp: int, method: str, path: str, query_string: str = "") -> str:
        """Generate HMAC SHA256 signature for Bitkub API"""
        message = f"{timestamp}{method}{path}"
        if query_string:
            message += f"?{query_string}"
        
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def get_order_history(
        symbol: str,
        page: str,
        limit: Optional[str] = None,
        cursor: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        pagination_type: Optional[str] = "page"
        ) -> Dict[Any, Any]:
        """
        Get order history from Bitkub API
        
        Parameters:
        - symbol: Trading symbol (e.g., "BTC_THB")
        - page: Page number
        - limit: Limit per page (default: 10, min: 1)
        - cursor: Base64 encoded cursor for keyset pagination
        - start: Start timestamp
        - end: End timestamp
        - pagination_type: "page" or "keyset" (default: "page")
        """
        
        endpoint = "/api/v3/market/my-order-history"
        timestamp = int(time.time() * 1000)
        
        # Build query parameters
        params = {
            "sym": symbol,
            "p": page,
        }
        
        if limit:
            params["lmt"] = limit
        if cursor:
            params["cursor"] = cursor
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if pagination_type:
            params["pagination_type"] = pagination_type
        
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        # Generate signature
        signature = generate_signature(timestamp, "GET", endpoint, query_string)    
        # Set headers
        headers = {
            "Accept": "application/json",
            "X-BTK-APIKEY": API_KEY,
            "X-BTK-TIMESTAMP": str(timestamp),
            "X-BTK-SIGN": signature
        }
        # Make request
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, params=params)    
        return response.json()
        
    result = get_order_history(
        symbol=symbol,
        page="1",
        limit=limit
    )
    return result
        
@csrf_exempt
def n8n_daily_update(request):
    """
    Endpoint triggered from n8n HTTP node.
    Expects ?symbol=BTC_THB or JSON body {"symbol": "BTC_THB"}.
    """
    api_key2 = request.headers.get('Authorization')
    if api_key2 != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)

    try:
        # 🔹 Get symbol from headers
        sym_thb = request.headers.get("Symbol")

        if not sym_thb:
            return JsonResponse({"error": "Missing 'Symbol' header"}, status=400)

        logger.info("Starting daily update for: %s", sym_thb)

        # Get transactions from Bitkub API
        transactions_data = get_purchased_transactions(sym_thb, 50)
        if "result" not in transactions_data or not transactions_data["result"]:
            return JsonResponse({
                "symbol": sym_thb,
                "status": "no_data",
                "message": "No transactions found."
            })

        transactions = transactions_data["result"]
        sym_thb = sym_thb.upper()
        sym = sym_thb.replace('_THB', '').upper()

        # Existing transaction IDs
        existing_ids = set(CryptoPurchase.objects.values_list('transaction', flat=True))

        added_count = 0
        skipped_count = 0
        added_orders = []

        for t in transactions:
            order_id = t["order_id"]

            # Skip if already exists
            if order_id in existing_ids:
                skipped_count += 1
                continue

            side = t["side"]
            purchase_price = float(t["rate"])
            fee = float(t["fee"])
            purchase_amount = float(t["amount"])
            timestamp = t["ts"]

            # Convert timestamp to readable date/time
            dt = datetime.fromtimestamp(timestamp / 1000)
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")

            # Calculate buy/sell logic
            if side == "buy":
                net_amount = purchase_amount - fee
                purchase_qty = net_amount / purchase_price
                final_amount = net_amount
            elif side == "sell":
                gross_amount = purchase_price * purchase_amount
                net_amount = (gross_amount - fee) * -1
                purchase_qty = purchase_amount * -1
                final_amount = net_amount
            else:
                continue

            # Insert into DB
            CryptoPurchase.objects.create(
                sym=sym,
                transaction=order_id,
                date=date_str,
                time=time_str,
                acc_pre_bal=0,
                crypto_pre_bal=0,
                acc_post_bal=0,
                crypto_post_bal=0,
                purchase_amount=final_amount,
                purchase_qty=purchase_qty,
                purchase_price=purchase_price,
                fear_greed=None,
                classification=None,
                spare_char1=side,
            )

            added_count += 1
            added_orders.append(order_id)

        logger.info("daily_update complete for %s | Added: %s | Skipped: %s", sym_thb, added_count, skipped_count)

        # ✅ Return clean JSON back to n8n
        return JsonResponse({
            "symbol": sym_thb,
            "status": "success",
            "added_count": added_count,
            "skipped_count": skipped_count,
            "added_orders": added_orders,
            "message": f"Added {added_count}, Skipped {skipped_count} transactions."
        }, status=200)

    except Exception as e:
        logger.exception("Error during daily_update for %s: %s", sym_thb, str(e))
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


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