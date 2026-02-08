import sqlite3
from datetime import datetime

DB_PATH = 'data/bot.db'

class Trade:
    def __init__(self, trade_id, symbol, side, price, quantity, timestamp):
        self.trade_id = trade_id
        self.symbol = symbol
        self.side = side
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

class Position:
    def __init__(self, position_id, symbol, side, entry_price, quantity, open_time, close_time=None):
        self.position_id = position_id
        self.symbol = symbol
        self.side = side
        self.entry_price = entry_price
        self.quantity = quantity
        self.open_time = open_time
        self.close_time = close_time

# Database setup

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        trade_id INTEGER PRIMARY KEY,
        symbol TEXT,
        side TEXT,
        price REAL,
        quantity REAL,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS positions (
        position_id INTEGER PRIMARY KEY,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        quantity REAL,
        open_time TEXT,
        close_time TEXT
    )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
