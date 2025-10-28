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

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io, base64

@csrf_exempt
def n8n_actionzone_symbol(request):
    # --- API key check ---
    api_key2 = request.headers.get('Authorization')
    symbol = (
        request.headers.get('Symbol')
        or request.GET.get('symbol')
        or request.POST.get('symbol')
        or 'BTCUSDT'
    )

    # Determine if it's API mode
    api_mode = api_key2 == f'Bearer {settings.APIKEY}'

    # Handle missing symbol for API
    if api_mode and not symbol:
        return JsonResponse({'error': 'Missing Symbol'}, status=400)

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

    # --- Generate Chart (only for web render) ---
    if not api_mode:
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
        return render(request, "actionzone_signal.html", {
            "latest_signals": latest_signals,
            "chart_base64": img_base64,
            "selected_symbol": symbol
        })

    # --- For API call (return JSON only) ---
    return JsonResponse({
        "symbol": symbol,
        "latest_signals": latest_signals
    })
    
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
    amount = 5000
    # binanceTh minimum 300 THB/order

    logger.info("Event: %s", event)
    logger.info("Symbol: %s", symbol)

    transaction = place_order(event, symbol, amount)

    data_update()

    # --- Return as JSON ---
    return JsonResponse({"Event": event, "Symbol": symbol, "Transaction": transaction})

def data_update():
    pass

def place_order(event, symbol, amount):
    
    base_url = "https://api.binance.th/api/v1/order"

    # --- Order Parameters ---
    timestamp = int(time.time() * 1000)

    params = {
        "symbol": symbol,           # BTC/THB trading pair
        "side": event,                # BUY or SELL
        "type": "MARKET",             # Market order
        "quoteOrderQty": amount,         # minimum 300 THB/order
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