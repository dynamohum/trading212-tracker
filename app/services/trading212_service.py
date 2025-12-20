from client import Trading212Client
from app.config import Config
import requests
import time

class Trading212Service:
    def __init__(self):
        self.keys, self.api_secret, self.mode = Config.load_credentials()
        self.current_account = Config.get_active_account(self.keys)
        self.instruments_cache = None
        self.instruments_last_fetch = 0
        
    def get_client(self):
        """Creates and returns a Trading212Client instance for the current account."""
        if not self.current_account or self.current_account not in self.keys:
            return None
            
        key = self.keys[self.current_account]
        return Trading212Client(key, api_secret=self.api_secret, mode=self.mode)

    def switch_account(self, account_name):
        """Switches the active account if valid."""
        if account_name in self.keys:
            self.current_account = account_name
            return True
        return False
        
    def get_account_status(self):
        """Returns current account status."""
        return {
            "current": self.current_account,
            "available": list(self.keys.keys())
        }

    def get_all_instruments(self):
        """
        Fetches all instruments, using a cache to reduce API calls.
        Cache valid for 24 hours.
        """
        now = time.time()
        if self.instruments_cache and (now - self.instruments_last_fetch < 86400):
            return self.instruments_cache
            
        client = self.get_client()
        if not client:
            return []
            
        try:
            # Manually fetch consistent with previous logic
            endpoint = "/api/v0/equity/metadata/instruments"
            url = f"{client.base_url}{endpoint}"
            res = requests.get(url, headers=client.headers, auth=client.auth)
            res.raise_for_status()
            data = res.json()
            
            self.instruments_cache = data if isinstance(data, list) else data.get("items", [])
            self.instruments_last_fetch = now
            return self.instruments_cache
        except Exception as e:
            print(f"Error fetching instruments: {e}")
            return []

    def find_instrument(self, ticker):
        """Finds a specific instrument in the cache."""
        instruments = self.get_all_instruments()
        for item in instruments:
             if item.get('ticker') == ticker or item.get('isin') == ticker:
                 return item
        return None

# Singleton instance
t212_service = Trading212Service()
