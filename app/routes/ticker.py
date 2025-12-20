from flask import Blueprint, jsonify, request
from app.services.trading212_service import t212_service
from app.utils.ticker_utils import normalize_to_yfinance
import yfinance as yf
import math

bp = Blueprint('ticker', __name__, url_prefix='/api/ticker')

@bp.route('/<ticker>/details')
def get_instrument_details(ticker):
    details = t212_service.find_instrument(ticker)
    return jsonify(details or {})

@bp.route('/<ticker>/dividends')
def get_dividends(ticker):
    client = t212_service.get_client()
    if not client:
        return jsonify({"error": "API Key not configured"}), 500
        
    try:
        dividends = client.get_dividends(limit=50, ticker=ticker)
        return jsonify({"items": dividends})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<ticker>/history')
def get_history(ticker):
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    try:
        yf_ticker = normalize_to_yfinance(ticker)
        stock = yf.Ticker(yf_ticker)
        hist = stock.history(period=period, interval=interval)
        
        # Fallback to original if normalized fails
        if hist.empty and yf_ticker != ticker:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)

        reset_hist = hist.reset_index()
        data = []
        
        for index, row in reset_hist.iterrows():
            d = row.get('Date') or row.get('Datetime')
            if d:
                # Cleaner helper
                def clean(val):
                    if val is None: return None
                    try:
                        if math.isnan(float(val)): return None
                    except: pass
                    return val

                data.append({
                    "time": d.isoformat(),
                    "open": clean(row['Open']),
                    "high": clean(row['High']),
                    "low": clean(row['Low']),
                    "close": clean(row['Close']),
                    "volume": clean(row['Volume'])
                })
                
        return jsonify({"items": data, "ticker": yf_ticker})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
