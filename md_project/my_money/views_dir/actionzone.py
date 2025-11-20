from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from ..models import CryptoPurchase, CryptoSymbolStatus, BinanceTransaction, CryptoAccumulatedAmount
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
from .crypto_views import get_fear_greed_index
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
import io, base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Can also use DEBUG

api_key = settings.BITKUB_API
api_secret = settings.BITKUB_SECRET_KEY

binance_api = settings.BINANCE_API
binance_secret_key = settings.BINANCE_SECRET_KEY

# Helper function for API key verification
def verify_api_key(request):
    api_key = request.headers.get('Authorization')
    if api_key != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)
    return None

@csrf_exempt
def n8n_start_process(request):
    unauthorized = verify_api_key(request)
    if unauthorized:
        return unauthorized

    symbol = request.headers.get('Symbol') #BTCUSDT
    sym = symbol.replace("USDT", "")
    symbol_thb = symbol.replace("USDT", "THB")
    choice = "2"
    latest_signals = actionzone_signal_calc(symbol, choice)
    logger.info("latest signals: %s", latest_signals)
    buy_signal = bool(latest_signals.get('Buy', False))
    sell_signal = bool(latest_signals.get('Sell', False))
    zone = latest_signals.get('Zone', '')
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    symbol_status_record = CryptoSymbolStatus.objects.filter(sym=symbol).first()
    if symbol_status_record is None:
        symbol_status_record = CryptoSymbolStatus.objects.create(
            sym=symbol,
            buy_status=False,
            sell_status=False,
            zone_color=zone,
            timestamp=timestamp,
            spare1='', spare2='', spare3=None, spare4=None
        )
        symbol_status_record = CryptoSymbolStatus.objects.filter(sym=symbol).first()
    
    # if buy_signal and not buy_status:
        # place order , symbol=BTCUSDT, amount = CryptoAccumulatedAmount
        # if buy success update accumulated_amount of symbol 
        # update CryptoAccumulatedAmount to 0
        # update CryptoSymbolStatus : buy_status to true, sell_status to false
        # update BinanceTransaction table with buy transaction
        
    # if sell_signal and not sell_status:
        # process to sell BTC amount , qty BTC quantity in Binance wallet
        # if sell success update accumulated_amount of symbol == amount of selling this transaction
        # update CryptoAccumulatedAmount: amount of selling this transaction, symbol 
        # update CryptoSymbolStatus : sell_status to true, buy_status to false
        # update BinanceTransaction table with sell transaction

    # get fear and greed index
    fear_greed, classification = get_fear_greed_index()
    amt = 50
    amt = ((100-int(fear_greed))*0.01)* amt #calculate amount of purchase 

    #has to find daily purchase routine
    # if zone == "Green" or zone == "Orange" or zone == "Yellow":
    #     event = "CONTINUE_BUY"
    #     # send order to function place order has to change BTCUSDT to BTCTHB
    #     transaction = place_order(event, symbol_thb, zone)
        
        # update transaction to BinanceTransaction table 
        # check THB in wallet if < accumulated_amount then send Notice to user

    # if zone == "Red" or zone == "Light Blue" or zone == "Blue":
    #     acc_amt_record = CryptoAccumulatedAmount.objects.filter(sym=sym).first()
    #     #has to change BTCUSDT to BTC
    #     #variable name symbol = "BTCUSDT", symbol_thb = "BTCTHB", sym = "BTC"
    #     if accumulated_amount_record is None:
    #         acc_amt_record = CryptoAccumulatedAmount.objects.create(
    #             sym=sym,
    #             accumulated_amount=amt,
    #             timestamp=timestamp,
    #             spare1='', spare2='', spare3=None, spare4=None
    #         )
    #     else
    #         # Update existing
    #         acc_amt = acc_amt + amt
    #         acc_amt_record.accumulated_amount = acc_amt
    #         acc_amt_record.timestamp = timestamp
    #         acc_amt_record.save()

        # calculated_amount to buy (apply with fear and greed index)
        # update CryptoAccumulatedAmount: table accumulated_amount = accumuldated_amount+calculated_amount 
        # check THB in wallet if < accumulated_amount then send Notice to user


    return JsonResponse({
        "symbol": symbol,
        "latest_signals": latest_signals,
        "buy_status": buy_status,
        "sell_status": sell_status
    })
    pass

@csrf_exempt
def n8n_actionzone_symbol(request):
    unauthorized = verify_api_key(request)
    if unauthorized:
        return unauthorized

    symbol = request.headers.get('Symbol')
    choice = "3" #API
    latest_signals = actionzone_signal_calc(symbol, choice)
    return JsonResponse({
        "symbol": symbol,
        "latest_signals": latest_signals
    })

@login_required
def actionzone_symbol1(request):
    symbol = (request.GET.get('symbol')
            or request.POST.get('symbol')
            or 'BTCUSDT'
        )
    choice = "1" # from Frontend
    latest_signals, img_base64 = actionzone_signal_calc(symbol, choice)

    return render(request, "actionzone_signal.html", {
        "latest_signals": latest_signals,
        "chart_base64": img_base64,
        "selected_symbol": symbol
    })

@csrf_exempt
def actionzone_signal_calc(symbol, choice):
    # # --- API key check ---
    # api_key2 = request.headers.get('Authorization')
    # symbol = (
    #     request.headers.get('Symbol')
    #     or request.GET.get('symbol')
    #     or request.POST.get('symbol')
    #     or 'BTCUSDT'
    # )

    # # Determine if it's API mode
    # api_mode = api_key2 == f'Bearer {settings.APIKEY}'

    # # Handle missing symbol for API
    # if api_mode and not symbol:
    #     return JsonResponse({'error': 'Missing Symbol'}, status=400)

    # --- Parameters ---
    limit = 500
    if choice == "2" or choice == "3":
        limit = 250
    interval = "1d"
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

    # --- Generate Chart (only for web render) ---
    if choice == "1":
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["Open time"], df["Close"], label="Close", linewidth=1)
        ax.plot(df["Open time"], df["EMA_fast"], label=f"EMA{ema_fast_period}", color="red", linewidth=1.5)
        ax.plot(df["Open time"], df["EMA_slow"], label=f"EMA{ema_slow_period}", color="blue", linewidth=1.5)
        ax.scatter(df.loc[df["Buy"], "Open time"], df.loc[df["Buy"], "Close"], color="green", marker="^", s=80)
        ax.scatter(df.loc[df["Sell"], "Open time"], df.loc[df["Sell"], "Close"], color="red", marker="v", s=80)
        ax.set_title("CDC Action Zone (EMA Crossover)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid(True)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        # Render frontend HTML
        return latest_signals, img_base64

    elif choice == "2" or choice == "3":
        return latest_signals
    
@csrf_exempt
def n8n_actionzone_execute(request):
    # --- API key check ---
    api_key2 = request.headers.get('Authorization')
    if api_key2 != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)

    # --- Get Event header ---
    event = request.headers.get('Event')
    symbol = request.headers.get('Symbol')
    symbol = symbol.replace("USDT", "THB")
    zone = request.headers.get('Zone')
    
    logger.info("Event: %s", event)
    logger.info("Symbol: %s", symbol)

    if zone == "Green" or zone == "Yellow" or zone == "Orange":
        transaction = place_order(combined, symbol, zone)    
        data_update()
        # --- Return as JSON ---
        return JsonResponse({"Event": event, "Symbol": symbol, "Transaction": transaction})
    else:
        return JsonResponse({"Event": "No transaction executed, Zone color is not Green or Yellow", "Zone": zone, "Symbol": symbol})

def data_update():
    pass

def get_binance_wallet_value():
    # ACCOUNT INFO

    base_url = "https://api.binance.th/api/v1/accountV2"

    timestamp = int(time.time() * 1000)
    params = {
        'timestamp': timestamp
    }

    # Create query string
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])

    # Generate signature using HMAC SHA256
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Add signature to params
    params['signature'] = signature

    # Add headers
    headers = {
        'Accept': 'application/json',
        'X-MBX-APIKEY': api_key
    }

    # Send GET request
    r = requests.get(base_url, params=params, headers=headers)
    account_data = r.json()

    balances = account_data.get('balances', [])
    table_data2 = []

    # === 2. For each asset, get last price and compute value ===
    for bal in balances:
        symbol = bal.get('asset')
        qty = float(bal.get('free', 0))

        # Skip if quantity is zero or the asset is THB
        if qty == 0:
            continue

        table_data2.append({
            'symbol': symbol,
            'qty': round(qty, 8),
        })


    btc_qty = None
    thb_amount = None

    for item in table_data2:
        if item['symbol'] == 'BTC':
            btc_qty = item['qty']
        elif item['symbol'] == 'THB':
            thb_amount = item['qty']

    # print("BTC Quantity to sell:", btc_qty)
    # print("THB Value to buy:", thb_value) 
    return btc_qty, thb_amount

def place_order(event, symbol, zone):
    
    base_url = "https://api.binance.th/api/v1/order"

    # --- Order Parameters ---
    timestamp = int(time.time() * 1000)

    btc_qty, thb_amount = get_binance_wallet_value()
    logger.info("BTC_QTY: %s", btc_qty)
    logger.info("THB_AMOUNT: %s", thb_amount)

    if (event == "BUY"):
        params = {
            "symbol": symbol,             # BTC/THB trading pair
            "side": event,                # BUY or SELL
            "type": "MARKET",             # Market order
            "quoteOrderQty": thb_amount,  # minimum 300 THB/order
            "timestamp": timestamp
        }
    elif (event == "CONTINUE_BUY"):
        amount_to_buy = 1000
        if zone == "Green":
            amount_to_buy = amount_to_buy * 0.3
        elif zone == "Yellow":
            amount_to_buy = amount_to_buy * 0.5
        else:
            amount_to_buy = amount_to_buy * 0.7

        params = {
            "symbol": symbol,             # BTC/THB trading pair
            "side": event,                # BUY or SELL
            "type": "MARKET",             # Market order
            "quoteOrderQty": amount_to_buy,  # minimum 300 THB/order
            "timestamp": timestamp
        }
    elif (event == "SELL"):
        params = {
            "symbol": symbol,             # BTC/THB trading pair
            "side": event,                # BUY or SELL
            "type": "MARKET",             # Market order
            "quantity": btc_qty,          # minimum ???
            "timestamp": timestamp
        }

    # --- Create query string ---
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])

    # --- Generate signature ---
    signature = hmac.new(binance_secret_key.encode('utf-8'),
                        query_string.encode('utf-8'),
                        hashlib.sha256).hexdigest()

    # --- Add signature to params ---
    params['signature'] = signature

    # --- Headers ---
    headers = {
        'Accept': 'application/json',
        'X-MBX-APIKEY': binance_api
    }

    # --- Send POST request ---
    try:
        r = requests.post(base_url, params=params, headers=headers)
        if not r.ok:
            print(f"Status: {r.status_code}")
            print("Response:", r.text)
        transaction = r.json()
        return transaction

        # Check for Binance API errors
        if isinstance(data, dict) and "code" in data and "msg" in data:
            print(f"Binance API Error {data['code']}: {data['msg']}")
        else:
            print(json.dumps(data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")

