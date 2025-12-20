import sqlite3
import datetime

conn = sqlite3.connect('portfolio_history.db')
c = conn.cursor()

print("--- Settings ---")
try:
    for row in c.execute('SELECT * FROM settings'):
        print(row)
except Exception as e:
    print(e)
    
print("\n--- History ---")
try:
    c.execute('SELECT count(*), min(timestamp), max(timestamp) FROM history')
    cnt, mint, maxt = c.fetchone()
    print(f"Count: {cnt}")
    if mint:
        print(f"Min: {datetime.datetime.fromtimestamp(mint)}")
        print(f"Max: {datetime.datetime.fromtimestamp(maxt)}")
    else:
        print("No history records")
except Exception as e:
    print(e)
conn.close()
