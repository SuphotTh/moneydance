from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, date, timedelta
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Sum, F, Q, Max
from decimal import Decimal
# from .crypto_utils import get_wallet_balances  # adjust path as needed
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from ..models import StockPurchased
from django.utils import timezone
from django.utils.timezone import make_aware
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
import matplotlib.pyplot as plt
import io, base64

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Can also use DEBUG

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
        portfolio = equity.get_portfolios()  # dictionary with 'portfolioList' and 'totalPortfolio'

        symbols = [item["symbol"] for item in portfolio["portfolioList"]]
        choice = "4"

        # Create a mapping from symbol -> latest signals
        for item in portfolio["portfolioList"]:
            symbol = item["symbol"]
            latest_signals = settrade_actionzone_signal_calc(symbol, choice)
            # Add latest signals to the portfolio item
            item['latest_signals'] = latest_signals

        return render(
            request,
            'settrade_acc_info.html',
            {
                'portfolio': portfolio,
                'account_info': account_info,
                'invx_acc_no': settings.INVX_ACC_NO
            }
        )

    except requests.exceptions.HTTPError as e:
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
        logger.exception("Unexpected error in portfolio view: %s", e)
        message = "An unexpected error occurred. Please try again later."

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

@csrf_exempt
def n8n_set_trigger(request):
    unauthorized = verify_api_key(request)
    if unauthorized:
        return unauthorized

    symbol = request.headers.get('Symbol')
    qty = request.headers.get('Qty')
    event = request.headers.get('Event')

    if not symbol or not qty:
        return JsonResponse({'error': 'Missing Symbol or Qty header'}, status=400)

    qty = int(qty)

    # place_order now always returns a dict or JsonResponse
    order_response = place_order(request, symbol, qty, event)

    # If order_response is already a JsonResponse (error), just return it directly
    if isinstance(order_response, JsonResponse):
        return order_response

    logger.info("order_response : %s", order_response)
    return JsonResponse({'OrderResponse': order_response})

def get_latest_market_price(symbol):
    try:
        investor = Investor(
            app_id=settings.INVX_APP_ID,
            app_secret=settings.INVX_APP_SECRET,
            broker_id=settings.INVX_BROKER_ID,
            app_code=settings.INVX_APP_CODE,
            is_auto_queue=False
        )

        mkt_data = investor.MarketData()
        res = mkt_data.get_quote_symbol(symbol)

        if not isinstance(res, dict):
            print(f"Unexpected response for {symbol}: {res}")
            return 0.0

        return float(res.get('last', 0.0) or 0.0)

    except Exception as e:
        print(f"Error fetching market price for {symbol}: {e}")
        return 0.0

def place_order(request, symbol, qty, event):
    try:
        purchase_price = get_latest_market_price(symbol)

        tomorrow = date.today() + timedelta(days=2)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        
        logger.info("event : %s", event)
        logger.info("sym : %s", symbol)
        logger.info("at : %s", purchase_price)
        logger.info("qty : %s", qty)
        logger.info("tomorrow_str : %s", tomorrow_str)

        if not purchase_price:
            return JsonResponse({'error': f'No price data found for {symbol}'}, status=404)

        investor = Investor(
            app_id=settings.INVX_APP_ID,
            app_secret=settings.INVX_APP_SECRET,
            broker_id=settings.INVX_BROKER_ID,
            app_code=settings.INVX_APP_CODE,
            is_auto_queue=False
        )

        equity = investor.Equity(account_no=settings.INVX_ACC_NO)

        if event == "Buy":
            order_response = equity.place_order(
                side=event,
                symbol=symbol,
                trustee_id_type="Local",
                volume=qty,
                qty_open=0,
                price=purchase_price,
                price_type="Limit",
                validity_type="Day",
                bypass_warning=False,
                valid_till_date=tomorrow_str,
                pin=settings.INVX_PIN
            )
        elif event == "Sell":
            # get accumulate quantity from Portfolio
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
            
            # Find actualVolume for AAPL80
            symbol_to_find = symbol
            actual_volume = next(
                (item['actualVolume'] for item in portfolio['portfolioList'] if item['symbol'] == symbol_to_find),
                None  # default value if not found
            )

            # get last price 
            selling_price = get_latest_market_price(symbol)
            # sell order 
            order_response = equity.place_order(
                side=event,
                symbol=symbol,
                trustee_id_type="Local",
                volume=actual_volume,
                qty_open=0,
                price=selling_price,
                price_type="Limit",
                validity_type="Day",
                bypass_warning=False,
                valid_till_date=tomorrow_str,
                pin=settings.INVX_PIN
            )

        # If successful, return plain dict
        return {
            'symbol': symbol,
            'status': 'Order placed successfully',
            'response': order_response
        }

    except SettradeError as e:
        return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

@login_required
def purchase_stock_report_page(request):
    # Get symbols from database as list
    db_symbols = list(StockPurchased.objects.values_list('symbol', flat=True).distinct())
    
    # Extra symbols to always include (optional)
    extra_symbols = ['AAPL80', 'GOOGL03', 'MSFT80', 'META80', 'NFLX80', 'BBL', 'KBANK', 'SCB']

    # Merge lists and remove duplicates while preserving order
    seen = set()
    symbols = []
    for s in db_symbols + extra_symbols:
        if s not in seen:
            seen.add(s)
            symbols.append(s)

    context = {
        'symbols': symbols,
        'sym': 'AAPL80',  # default symbol
    }
    return render(request, 'purchase_stock_report.html', context)

@login_required
def purchase_stock_report(request):
    sym = request.GET.get('sym', 'AAPL80')  # default AAPL
    page = int(request.GET.get('page', 1))

    purchases = StockPurchased.objects.filter(symbol=sym).order_by('-date', '-time')
    paginator = Paginator(purchases, 8)
    page_obj = paginator.get_page(page)

    status = update_stock_purchased() #update database

    logger.info("Symbol : %s", sym)
    logger.info("Status : %s", status)
    
    acc_last_price = Decimal(get_latest_market_price(sym))
    acc_total_qty = 0
    acc_total_value = 0
    total_cost = 0
    for p in purchases:
        if p.side == "Sell":
            p.qty *= -1
        acc_total_qty += p.qty
        acc_total_value = acc_total_value + (acc_last_price * p.qty)
        total_cost = total_cost + (p.price * p.qty) + p.brokerage_fee + p.trading_fee + p.clearing_fee

    
    logger.info("Total Cost : %s", total_cost)
    logger.info("QTY : %s", acc_total_qty)
    logger.info("Value : %s", acc_total_value)
    logger.info("Last Price : %s", acc_last_price)
    # Calculate P&L if you have market price API
    market_price = acc_last_price
    p_and_l = acc_total_qty * market_price - total_cost if acc_last_price > 0 else 0
    percent = (p_and_l / total_cost * 100) if total_cost > 0 else 0

    data = {
        'page_obj': [
            {
                'id': p.id,
                'date': p.date.strftime('%Y-%m-%d'),
                'time': p.time.strftime('%H:%M:%S'),
                'symbol': p.symbol,
                'acc_no': p.acc_no,
                'order_no': p.order_no,
                'side': p.side,
                'qty': float(p.qty),
                'price': float(p.price),
                'brokerage_fee': float(p.brokerage_fee or 0),
                'trading_fee': float(p.trading_fee or 0),
                'clearing_fee': float(p.clearing_fee or 0),
            } for p in page_obj
        ],
        'pagination': {
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
        },
        'acc_total_qty': float(acc_total_qty),
        'acc_total_value': float(acc_total_value),
        'acc_last_price': float(acc_last_price),
        'total_cost': float(total_cost),
        'p_and_l': float(p_and_l),
        'percent': float(percent),
    }

    return JsonResponse(data)

@csrf_exempt
def n8n_update_stock_purchased(request):
    """
    Fetch trades from the Investor API for a specific date and insert them into StockPurchased.
    Skip trades that already exist based on trade_no (unique key).
    """
    unauthorized = verify_api_key(request)
    if unauthorized:
        return unauthorized
    
    return update_stock_purchased()

def update_stock_purchased():
    try:
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
            return {'status': 'no_trades'}

        for trade in trades:
            trade_no = trade.get("tradeNo")

            # Skip existing trades
            if StockPurchased.objects.filter(trade_no=trade_no).exists():
                continue

            trade_time_full = trade.get("tradeTime")  # e.g., "2025-10-27T19:55:22"

            if trade_time_full and "T" in trade_time_full:
                trade_date, trade_time = trade_time_full.split("T")  # date = "2025-10-27", time = "19:55:22"
            else:
                trade_date, trade_time = None, None
            stock_record = StockPurchased.objects.create(
                symbol=trade.get("symbol"),
                date=trade_date,
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
            logger.info(f"Inserted trade {trade_no} ({trade.get('symbol')})")

        return JsonResponse({'status': 'success'})

    except SettradeError as e:
        logger.error(f"Settrade API error: {e}")
        return {'status': 'error', 'error': str(e)}

    except Exception as e:
        logger.exception("Unexpected error in n8n_update_stock_purchased")
        return {'status': 'error', 'error': str(e)}

def settrade_actionzone_signal1(request):
    symbol = (
        request.headers.get('Symbol')
        or request.GET.get('symbol')
        or 'SET'
        )
    choice = "1"
    symbol, latest_signals, img_base64 = settrade_actionzone_signal_calc(symbol, choice)
    return render(request, "settrade_actionzone_signal.html", {
        "latest_signals": latest_signals,
        "chart_base64": img_base64,
        "selected_symbol": symbol,
        "interesting_lists": interesting_list(), 
    })

def settrade_actionzone_signal2(request):
    symbol = (
        request.headers.get('Symbol')
        or request.GET.get('symbol')
        or 'SET'
    )
    choice = "2"

    try:
        symbol, latest_signals, img_base64 = settrade_actionzone_signal_calc(symbol, choice)
        return render(
            request,
            "settrade_actionzone_signal2.html",
            {
                "latest_signals": latest_signals,
                "chart_base64": img_base64,
                "selected_symbol": symbol,
            },
        )

    except ValueError as ve:
        # custom "symbol not found" or "no data" error
        return render(
            request,
            "settrade_actionzone_signal2.html",
            {
                "error_message": str(ve),
                "selected_symbol": symbol,
                "latest_signals": None,
                "chart_base64": None,
            },
        )

    except Exception as e:
        # other unexpected errors
        logger.exception("Error in settrade_actionzone_signal2")
        return render(
            request,
            "settrade_actionzone_signal2.html",
            {
                "error_message": f"Unexpected error: {str(e)}",
                "selected_symbol": symbol,
                "latest_signals": None,
                "chart_base64": None,
            },
        )

@csrf_exempt
def n8n_settrade_actionzone_signal(request):
    unauthorized = verify_api_key(request)
    if unauthorized:
        return unauthorized

    symbol = request.headers.get('Symbol')
    choice = "3" #API
    latest_signals = settrade_actionzone_signal_calc(symbol, choice)
    return JsonResponse({
        "symbol": symbol,
        "latest_signals": latest_signals
    })
    
def settrade_actionzone_signal_calc(symbol, choice):

    logger.info("SYMBOL : %s", symbol)

    # --- Initialize Investor ---
    investor = Investor(
        app_id=settings.INVX_APP_ID,
        app_secret=settings.INVX_APP_SECRET,
        broker_id=settings.INVX_BROKER_ID,
        app_code=settings.INVX_APP_CODE,
        is_auto_queue=False
    )

    equity = investor.Equity(account_no=settings.INVX_ACC_NO)
    market = investor.MarketData()

    # --- Fetch data from Settrade ---
    limit = 350
    if choice == "3" or choice == "4":
        limit = 250
    res = market.get_candlestick(
        symbol=symbol,
        interval="1d",
        limit=limit,
        normalized=True,
    )

    # === Convert to DataFrame ===
    df = pd.DataFrame({
        "Open": res.get("open", []),
        "High": res.get("high", []),
        "Low": res.get("low", []),
        "Close": res.get("close", []),
        "Volume": res.get("volume", []),
        "Time": res.get("time", [])
    })

    if df.empty:
        return JsonResponse({"error": "No candlestick data returned"}, status=400)

    # Convert timestamp to datetime
    df["Open time"] = pd.to_datetime(df["Time"], unit="s")  # Settrade uses seconds

    # --- Calculate EMAs ---
    ema_fast_period = 12
    ema_slow_period = 26
    # ema_fast_period = 25
    # ema_slow_period = 100
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

    # --- Latest Signal ---
    latest = df.tail(1)[["Open time", "Close", "EMA_fast", "EMA_slow", "Zone", "Buy", "Sell"]]
    latest.insert(0, 'Symbol', symbol)
    latest.rename(columns={"Open time": "Open_time"}, inplace=True)
    latest_signals = latest.to_dict(orient="records")[0]

    # --- If frontend, generate chart ---
    if choice == "1" or choice == "2":
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["Open time"], df["Close"], label="Close", linewidth=1)
        ax.plot(df["Open time"], df["EMA_fast"], label=f"EMA{ema_fast_period}", color="red", linewidth=1.5)
        ax.plot(df["Open time"], df["EMA_slow"], label=f"EMA{ema_slow_period}", color="blue", linewidth=1.5)
        ax.scatter(df.loc[df["Buy"], "Open time"], df.loc[df["Buy"], "Close"], color="green", marker="^", s=80)
        ax.scatter(df.loc[df["Sell"], "Open time"], df.loc[df["Sell"], "Close"], color="red", marker="v", s=80)
        ax.set_title(f"Settrade Action Zone for {symbol}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (THB)")
        ax.legend()
        ax.grid(True)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return symbol, latest_signals, img_base64

    elif choice == "3" or choice == "4":
        return latest_signals

def interesting_list():
    interesting_lists = [
        "ADVANC",
        "AOT",
        "BAY",
        "BBL",
        "BDMS",
        "BH",
        "CPALL",
        "CPN",
        "CRC",
        "KBANK",
        "KKP",
        "KTC",
        "MFEC",
        "MINT",
        "SCB",
        "TISCO",
        "TLI",
        "AAPL80",
        "AMD80",
        "AMZN80",
        "ASML01",
        "BABA06",
        "BRKB80",
        "CRWD06",
        "GOOGL03",
        "HERMES80",
        "KO80",
        "LVMH01",
        "META80",
        "MSFT80",
        "NDAQ06",
        "NFLX80",
        "ORCL06",
        "PANW80",
        "PINGAN80",
        "PLTR03",
        "SINGTEL80",
    ]

    return interesting_lists

@login_required
def settrade_signal_list(request):
    symbols = interesting_list()
    choice = "4"
    # logger.info("Symbol : %s", symbols)

    signal_list = []
    # --- Loop symbols and get EMA signals ---
    for symbol in symbols:
        latest_signals = settrade_actionzone_signal_calc(symbol, choice)
        signal_list.append(latest_signals)
        # logger.info("Symbol :%s", latest_signals)

    # --- Return to frontend ---
    return render(request, "settrade_signal_list.html", {
        "signal_list": signal_list,
    })
