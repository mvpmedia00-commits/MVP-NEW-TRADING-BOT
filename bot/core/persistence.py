"""Persistence manager for state recovery"""
from typing import Dict, List, Optional
from datetime import datetime
from ..models.database import Trade, Position, BotState, init_db, get_engine
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PersistenceManager:
    def __init__(self, db_url=None):
        engine = get_engine(db_url)
        init_db(engine)
        self.Session = init_db(engine)
        logger.info("Persistence manager initialized")
    
    def save_position(self, symbol: str, side: str, entry_price: float, quantity: float, broker: str):
        session = self.Session()
        try:
            pos = session.query(Position).filter_by(symbol=symbol).first()
            if pos:
                pos.side = side
                pos.entry_price = entry_price
                pos.quantity = quantity
                pos.updated_at = datetime.utcnow()
            else:
                pos = Position(symbol=symbol, side=side, entry_price=entry_price, 
                             quantity=quantity, broker=broker)
                session.add(pos)
            session.commit()
            logger.info(f"Position saved: {symbol}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving position: {e}")
        finally:
            session.close()
    
    def close_position(self, symbol: str, exit_price: float, pnl: float):
        session = self.Session()
        try:
            pos = session.query(Position).filter_by(symbol=symbol).first()
            if pos:
                trade = Trade(
                    symbol=pos.symbol, side=pos.side, entry_price=pos.entry_price,
                    exit_price=exit_price, quantity=pos.quantity, pnl=pnl,
                    entry_time=pos.opened_at, exit_time=datetime.utcnow(),
                    status='closed', broker=pos.broker
                )
                session.add(trade)
                session.delete(pos)
                session.commit()
                logger.info(f"Position closed: {symbol}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error closing position: {e}")
        finally:
            session.close()
    
    def get_open_positions(self) -> List[Dict]:
        session = self.Session()
        try:
            positions = session.query(Position).all()
            return [{
                'symbol': p.symbol, 'side': p.side, 'entry_price': p.entry_price,
                'quantity': p.quantity, 'broker': p.broker, 'opened_at': p.opened_at
            } for p in positions]
        finally:
            session.close()
    
    def save_state(self, key: str, value: str):
        session = self.Session()
        try:
            state = session.query(BotState).filter_by(key=key).first()
            if state:
                state.value = value
                state.updated_at = datetime.utcnow()
            else:
                state = BotState(key=key, value=value)
                session.add(state)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving state: {e}")
        finally:
            session.close()
    
    def get_state(self, key: str) -> Optional[str]:
        session = self.Session()
        try:
            state = session.query(BotState).filter_by(key=key).first()
            return state.value if state else None
        finally:
            session.close()
