import os

class Config:
    """Application configuration and credentials management."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    DB_FILE = "portfolio_history.db"

    @staticmethod
    def load_credentials():
        """
        Load Trading212 credentials from environment variables or 'api' file.
        Returns keys dict, api_secret, and mode.
        """
        keys = {}
        api_secret = os.environ.get("TRADING212_API_SECRET")
        mode = os.environ.get("TRADING212_MODE", "demo")
        
        # Environment variables
        if os.environ.get("TRADING212_ISA_KEY"):
             keys['ISA'] = os.environ.get("TRADING212_ISA_KEY")
        if os.environ.get("TRADING212_INVEST_KEY"):
             keys['INVEST'] = os.environ.get("TRADING212_INVEST_KEY")
        if os.environ.get("TRADING212_API_KEY"):
             keys['DEFAULT'] = os.environ.get("TRADING212_API_KEY")

        # File loading (legacy support)
        try:
            if os.path.exists("api"):
                with open("api", "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        
                        if "TRADING212_ISA_KEY" in line and "=" in line:
                             keys['ISA'] = line.split("=")[1].strip().strip("'").strip('"')
                        elif "TRADING212_INVEST_KEY" in line and "=" in line:
                             keys['INVEST'] = line.split("=")[1].strip().strip("'").strip('"')
                        elif "TRADING212_API_KEY" in line and "=" in line:
                             keys['DEFAULT'] = line.split("=")[1].strip().strip("'").strip('"')
                        elif "TRADING212_API_SECRET" in line and "=" in line:
                            api_secret = line.split("=")[1].strip().strip("'").strip('"')
                        elif "TRADING212_MODE" in line and "=" in line:
                            mode = line.split("=")[1].strip().strip("'").strip('"').lower()
        except Exception as e:
            print(f"Error loading api file: {e}")
                
        return keys, api_secret, mode

    @staticmethod
    def get_active_account(keys, requested_account=None):
        """Determines the active account key."""
        if requested_account and requested_account in keys:
            return requested_account
        return next(iter(keys)) if keys else None
