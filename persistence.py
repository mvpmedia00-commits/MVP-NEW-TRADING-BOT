import sqlite3
from database import DB_PATH, Trade, Position

class PersistenceManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def save_trade(self, trade: Trade):
        self.cursor.execute('''INSERT INTO trades (symbol, side, price, quantity, timestamp) VALUES (?, ?, ?, ?, ?)''',
            (trade.symbol, trade.side, trade.price, trade.quantity, trade.timestamp))
        self.conn.commit()

    def save_position(self, position: Position):
        self.cursor.execute('''INSERT INTO positions (symbol, side, entry_price, quantity, open_time, close_time) VALUES (?, ?, ?, ?, ?, ?)''',
            (position.symbol, position.side, position.entry_price, position.quantity, position.open_time, position.close_time))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_open_positions(self):
        self.cursor.execute('''SELECT * FROM positions WHERE close_time IS NULL''')
        return self.cursor.fetchall()

    def update_position_close(self, position_id, close_time):
        self.cursor.execute('''UPDATE positions SET close_time = ? WHERE position_id = ?''', (close_time, position_id))
        self.conn.commit()
