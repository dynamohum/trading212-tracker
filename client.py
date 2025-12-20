import requests
from typing import List, Dict, Any, Optional

class Trading212Client:
    def __init__(self, api_key: str, api_secret: Optional[str] = None, mode: str = 'demo'):
        """
        Initialize the Trading212 Client.

        Args:
            api_key: Your Trading212 API Key.
            api_secret: Your Trading212 API Secret (optional).
            mode: 'demo' or 'live'. Defaults to 'demo'.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        if mode == 'live':
            self.base_url = "https://live.trading212.com"
        else:
            self.base_url = "https://demo.trading212.com"
        
        if self.api_secret:
            self.auth = requests.auth.HTTPBasicAuth(self.api_key, self.api_secret)
            self.headers = {}
        else:
            self.auth = None
            self.headers = {
                "Authorization": self.api_key
            }

    def _paginated_request(self, endpoint: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Internal helper for cursor-based pagination.
        """
        url =f"{self.base_url}{endpoint}"
        all_items = []
        params = {"limit": limit}
        
        current_url = url
        current_params = params
        
        while True:
            # If current_params is None, checking url for params or use empty
            # But requests handles params merged with url params typically? 
            # If using next_page_path which is relative and has query params, we shouldn't pass separate params dict again.
            
            call_params = current_params if current_params else {}
            
            response = requests.get(current_url, headers=self.headers, auth=self.auth, params=call_params)
            response.raise_for_status()
            data = response.json()
            
            items = []
            next_page_path = None
            
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("items", [])
                next_page_path = data.get("nextPagePath")
            
            all_items.extend(items)
            
            if not next_page_path:
                break
                
            # Prepare for next iteration
            # nextPagePath is relative, e.g. /api/v0/...
            current_url = f"{self.base_url}{next_page_path}"
            current_params = None # Parameters are encoded in the nextPagePath
            
        return all_items

    def get_all_positions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetches all open positions using cursor-based pagination.
        Endpoint: /api/v0/equity/positions (documented usually, sometimes found as portfolio)
        """
        return self._paginated_request("/api/v0/equity/positions", limit=limit)

    def get_dividends(self, limit: int = 50, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches dividend history.
        Endpoint: /api/v0/equity/history/dividends
        """
        endpoint = "/api/v0/equity/history/dividends"
        url = f"{self.base_url}{endpoint}"
        params = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        data = response.json()
        
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("items", [])
            
        # Optional client-side filter if API doesn't support strict ticker param in all versions
        if ticker:
            items = [d for d in items if d.get('ticker') == ticker or d.get('instrumentCode') == ticker]
            
        return items
