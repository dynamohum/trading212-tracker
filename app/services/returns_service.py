import datetime

class ReturnsService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.periods = {
            "1h": 3600,
            "24h": 24 * 3600,
            "7d": 7 * 24 * 3600,
            "30d": 30 * 24 * 3600,
            "90d": 90 * 24 * 3600,
            "1y": 365 * 24 * 3600
        }

    def calculate_returns(self):
        """
        Calculates percentage returns for standard periods.
        Returns a dict e.g. {"24h": 1.5, "7d": -0.5}
        """
        results = {}
        
        latest = self.db_manager.get_latest_history()
        if not latest:
            return results
            
        current_val, current_ts = latest
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        
        for key, seconds in self.periods.items():
            target_time = now - seconds
            past_record = self.db_manager.get_history_before(target_time)
            
            if past_record:
                past_val = past_record[0]
                if past_val != 0:
                     change_pct = ((current_val - past_val) / past_val) * 100
                     results[key] = change_pct
                     
        return results
