from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
# from ..models import Transaction, Category, Payee, Account_type, Account_name, Account_detail
from datetime import datetime, date, timedelta
from django.db import transaction
from django.conf import settings
import csv
import re
import io
import json
import time
import hmac
import hashlib
import requests
import pandas as pd

api_key = 'f4e233579193251e56195194d728881d0f054fd1909ed59771da3366d631d8d7'
api_secret = '5a82abe75e9d46bbb11f9fd4ae2c85d00aa7f3e433bf4a3f9fb1819a50a4e0aew3A3kLS03f8fuaGI76I0f9w4vbZc'

@login_required
def wallet_balances(request):
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
    # print(wallet)


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
    ticker_response = requests.get(url, headers=headers, data=body)
    ticker = ticker_response.json()
    # print(ticker)

    ticker_prices = {
        item['symbol'].replace('_THB', ''): float(item['last'])
        for item in ticker
    }
    ticker_prices['THB'] = 1

    # print(ticker_prices)
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

    # Convert to DataFrame and display
    df = pd.DataFrame(table_data)
    print(df.to_string(index=False))

    return render(request, 'crypto.html', {
        'data': table_data,
        'total_value': total_value })

@login_required
def place_order(request):
    # Configuration
    timestamp = str(int(time.time() * 1000))
    method = 'POST'
    request_path = '/api/v3/market/place-bid'

    # Order data
    order_data = {
        'sym': 'btc_thb',     # Trading pair
        'amt': 100,          # Amount in THB
        'rat': 0,       # Rate (price per BTC)
        'typ': 'market'        # Order type
    }

    # Convert body to JSON string
    body = json.dumps(order_data, separators=(',', ':'))  # Compact JSON

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

    response = requests.post(url, headers=headers, data=body)
    print(response.json())

    # return render(request, 'crypto.html', {'data': respond })    

@csrf_exempt
def n8n_trigger(request):
    api_key2 = request.headers.get('Authorization')
    if api_key2 != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)
    if request.method == 'POST':
        data = json.loads(request.body)
        # Do something with the data
            
        timestamp = str(int(time.time() * 1000))
        method = 'POST'
        request_path = '/api/v3/market/place-bid'

        # Order data
        order_data = {
            'sym': 'btc_thb',     # Trading pair
            'amt': 120,          # Amount in THB
            'rat': 0,       # Rate (price per BTC)
            'typ': 'market'        # Order type
        }

        # Convert body to JSON string
        body = json.dumps(order_data, separators=(',', ':'))  # Compact JSON

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

        response = requests.post(url, headers=headers, data=body)
        print(response.json())
        print("Received from n8n:", data)
        return JsonResponse({'status': response.json()})

    return JsonResponse({'error': 'Invalid request'}, status=400)


