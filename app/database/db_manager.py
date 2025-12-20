import sqlite3
import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # History table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    timestamp REAL,
                    total_value REAL,
                    currency TEXT
                )
            ''')
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            # Default tracking setting
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('tracking_enabled', 'false'))
            conn.commit()

    def get_setting(self, key, default=None):
        """Retrieve a setting value."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key, value):
        """Update or insert a setting value."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
            conn.commit()

    def add_history_record(self, total_value, currency):
        """Record portfolio value snapshot."""
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        with self.get_connection() as conn:
            conn.execute('INSERT INTO history (timestamp, total_value, currency) VALUES (?, ?, ?)', (now, total_value, currency))

    def get_latest_history(self):
        """Get the most recent history record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT total_value, timestamp FROM history ORDER BY timestamp DESC LIMIT 1')
            return cursor.fetchone()

    def get_history_before(self, timestamp):
        """Get the latest history record closest to but before the given timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT total_value FROM history WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1', (timestamp,))
            return cursor.fetchone()
