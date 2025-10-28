from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, date, timedelta
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from decimal import Decimal
# from .crypto_utils import get_wallet_balances  # adjust path as needed
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from ..models import StockPurchased
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q
import csv
import re
import io
import json
import time
import hmac
import hashlib
import requests
import pandas as pd
import logging

import settrade_v2
from settrade_v2 import Investor
from pprint import pprint
from settrade_v2.errors import SettradeError
from django.http import JsonResponse
from pprint import pprint

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Can also use DEBUG

# @login_required
# def portfolio(request):
    
#     investor = Investor(
#         app_id=settings.SETTRADE_APP_ID,
#         app_secret=settings.SETTRADE_APP_SECRET,
#         broker_id=settings.SETTRADE_BROKER_ID,
#         app_code=settings.SETTRADE_APP_CODE,
#         is_auto_queue=False
#     )

#     equity = investor.Equity(account_no= settings.INVX_ACC_NO)
#     account_info = equity.get_account_info()
    
#     equity = investor.Equity(account_no=settings.INVX_ACC_NO)
#     portfolio = equity.get_portfolios()
    
#     return render(request, 'settrade_acc_info.html', {'portfolio': portfolio, 'account_info': account_info})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

@login_required
def portfolio(request):
    try:
        investor = Investor(
            app_id=settings.INVX_APP_ID,
            app_secret=settings.INVX_APP_SECRET,
            broker_id=settings.INVX_BROKER_ID,
            app_code=settings.INVX_APP_CODE,
            is_auto_queue=False
        )

        equity = investor.Equity(account_no=settings.INVX_ACC_NO)
        account_info = equity.get_account_info()
        portfolio = equity.get_portfolios()

        return render(
            request,
            'settrade_acc_info.html',
            {'portfolio': portfolio , 'account_info': account_info, 'invx_acc_no': settings.INVX_ACC_NO}
        )

    except requests.exceptions.HTTPError as e:
        # If the server explicitly returns 503
        if e.response.status_code == 503:
            logger.warning("Settrade server maintenance (503): %s", e)
            message = "The Settrade server is currently under maintenance. Please try again later."
        else:
            logger.error("HTTP error while retrieving portfolio: %s", e)
            message = f"An error occurred: {e}"

    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error while contacting Settrade: %s", e)
        message = "Unable to connect to the Settrade server. Please check your internet connection or try again later."

    except Exception as e:
        # Catch all other unexpected errors
        logger.exception("Unexpected error in portfolio view: %s", e)
        message = "An unexpected error occurred. Please try again later."

    # Return a friendly error page
    return render(
        request,
        'settrade_acc_info.html',
        {'error_message': message}
    )


# Helper function for API key verification
def verify_api_key(request):
    api_key = request.headers.get('Authorization')
    if api_key != f'Bearer {settings.APIKEY}':
        return JsonResponse({'error': 'Unauthorized Access'}, status=401)
    return None


# @csrf_exempt
# def n8n_kbank_trigger(request):
#     unauthorized = verify_api_key(request)
#     if unauthorized:
#         return unauthorized

#     symbol = "KBANK"
#     return place_order(request, symbol)


# @csrf_exempt
# def n8n_bbl_trigger(request):
#     unauthorized = verify_api_key(request)
#     if unauthorized:
#         return unauthorized

#     symbol = "BBL"
#     return place_order(request, symbol)


# @csrf_exempt
# def n8n_scb_trigger(request):
#     unauthorized = verify_api_key(request)
#     if unauthorized:
#         return unauthorized

#     symbol = "SCB"
#     return place_order(request, symbol)

@csrf_exempt
def n8n_set_trigger(request):
    unauthorized = verify_api_key(request)
    if unauthorized:
        return unauthorized

    symbol = request.headers.get('Symbol')
    qty = request.headers.get('Qty')

    if not symbol or not qty:
        return JsonResponse({'error': 'Missing Symbol or Qty header'}, status=400)

    qty = int(qty)

    order_response = place_order(request, symbol, qty)
    # If order_response is a JsonResponse, it means an error occurred
    if isinstance(order_response, JsonResponse):
        return order_response

    logger.info("order_response : %s", order_response)

    return JsonResponse({'OrderResponse': order_response})


def place_order(request, symbol, qty):
    try:
        # Initialize Investor
        investor = Investor(
            app_id=settings.INVX_APP_ID,
            app_secret=settings.INVX_APP_SECRET,
            broker_id=settings.INVX_BROKER_ID,
            app_code=settings.INVX_APP_CODE,
            is_auto_queue=False
        )

        # Get latest market price
        mkt_data = investor.MarketData()
        res = mkt_data.get_quote_symbol(symbol)
        purchase_price = res.get('last')

        logger.info("buy : %s", symbol)
        logger.info("at : %s", purchase_price)
        logger.info("qty : %s", qty)

        if not purchase_price:
            return None, JsonResponse({'error': f'No price data found for {symbol}'}, status=404)

        # Proceed to place order
        equity = investor.Equity(account_no=settings.INVX_ACC_NO)

        order_response = equity.place_order(
            side= "Buy",
            symbol= symbol,
            trustee_id_type= "Local",
            volume= qty,
            qty_open= 0,
            price= purchase_price,  # Fixed for testing
            price_type= "Limit",
            validity_type= "Date",
            bypass_warning= False,
            valid_till_date= "2025-10-31",
            pin=settings.INVX_PIN
        )

        return order_response

    except SettradeError as e:
        return None, JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        return None, JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


@csrf_exempt
def n8n_update_stock_purchased(request):
    """
    Fetch trades from the Investor API, filter by tradeDate, and insert into StockPurchased table.
    Skip trades that already exist based on trade_no (unique key).
    """
    try:
        date = request.headers.get("Date")  # e.g., "2025-10-27"
        if not date:
            return JsonResponse({'error': 'Missing Date header'}, status=400)

        # Initialize Investor
        investor = Investor(
            app_id=settings.INVX_APP_ID,
            app_secret=settings.INVX_APP_SECRET,
            broker_id=settings.INVX_BROKER_ID,
            app_code=settings.INVX_APP_CODE,
            is_auto_queue=False
        )

        equity = investor.Equity(account_no=settings.INVX_ACC_NO)
        trades = equity.get_trades()

        if not trades:
            logger.warning("No trades returned from API.")
            return JsonResponse({'error': 'No trades found'}, status=404)

        # Filter trades for today
        trades_today = [t for t in trades if t.get("tradeDate") == date]

        if not trades_today:
            logger.info(f"No trades found for date {date}")
            return JsonResponse({'status': 'no_trades', 'date': date})

        inserted_trades = []
        skipped_trades = []

        for trade in trades_today:
            trade_no = trade.get("tradeNo")

            # Skip if trade_no already exists
            if StockPurchased.objects.filter(trade_no=trade_no).exists():
                skipped_trades.append(trade_no)
                logger.info(f"Trade {trade_no} already exists. Skipping insert.")
                continue

            trade_time_full = trade.get("tradeTime")  # e.g., "2025-10-27T19:55:22"
            trade_time = trade_time_full.split("T")[1] if trade_time_full and "T" in trade_time_full else None

            stock_record = StockPurchased.objects.create(
                symbol=trade.get("symbol"),
                date=trade.get("tradeDate"),
                time=trade_time,
                price=trade.get("px"),
                qty=trade.get("qty"),
                order_no=trade.get("orderNo"),
                trade_no=trade_no,
                side=trade.get("side"),
                brokerage_fee=trade.get("brokerageFee"),
                trading_fee=trade.get("tradingFee"),
                clearing_fee=trade.get("clearingFee"),
            )
            inserted_trades.append(stock_record.id)
            logger.info(f"Inserted trade {trade_no} for symbol {trade.get('symbol')}")

        return JsonResponse({
            'status': 'success',
            'date': date,
            'inserted': inserted_trades,
            'skipped': skipped_trades
        })

    except SettradeError as e:
        logger.error(f"Settrade API error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        logger.exception("Unexpected error in n8n_update_stock_purchased")
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


