import time
import json
import threading
import datetime
import sqlite3
from app.services.trading212_service import t212_service

class TrackerService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self._stop_event = threading.Event()
        self._thread = None

    def start_background_tracking(self):
        """Starts the background tracking thread."""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._tracker_loop, daemon=True)
            self._thread.start()
            print("Background tracker started.")

    def stop_background_tracking(self):
        """Stops the background tracking thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

    def fetch_portfolio_value(self):
        """Calculates total portfolio value excluding hidden tickers."""
        client = t212_service.get_client()
        if not client:
            return None, None
            
        try:
            positions = client.get_all_positions()
            
            # Get hidden tickers
            hidden_json = self.db_manager.get_setting('hidden_tickers', '[]')
            try:
                hidden_tickers = json.loads(hidden_json)
            except:
                hidden_tickers = []
                
            total_val = 0.0
            currency = 'GBP' # Default
            
            for pos in positions:
                # Check ticker to exclude
                ticker = pos.get('instrument', {}).get('ticker') or pos.get('ticker')
                if ticker in hidden_tickers:
                    continue

                if 'walletImpact' in pos: # New API format
                    total_val += float(pos['walletImpact'].get('currentValue', 0))
                    if 'currency' in pos['walletImpact']:
                        currency = pos['walletImpact']['currency']
                else: # Fallback
                    qty = float(pos.get('quantity', 0))
                    price = float(pos.get('currentPrice', 0))
                    total_val += qty * price
                    
            return total_val, currency
        except Exception as e:
            print(f"Error fetching portfolio value: {e}")
            return None, None

    def _tracker_loop(self):
        """Internal loop for background tracking."""
        while not self._stop_event.is_set():
            try:
                enabled = self.db_manager.get_setting('tracking_enabled') == 'true'
                if enabled:
                    val, curr = self.fetch_portfolio_value()
                    if val is not None:
                        self.db_manager.add_history_record(val, curr)
                        print(f"[{datetime.datetime.now()}] Recorded history: {val} {curr}")
                
                # Check stop event periodically during sleep
                for _ in range(300): # 5 minutes sleep
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Tracker error: {e}")
                time.sleep(60)
