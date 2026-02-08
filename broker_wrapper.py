import ccxt
import time

class BrokerWrapper:
    def __init__(self, exchange_id, api_key, api_secret, testnet=False):
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
            'secret': api_secret,
            'test': testnet
        })

    def safe_request(self, method, *args, retries=3, delay=2, **kwargs):
        for attempt in range(retries):
            try:
                return getattr(self.exchange, method)(*args, **kwargs)
            except Exception as e:
                print(f"Broker error: {e}, retry {attempt+1}/{retries}")
                time.sleep(delay)
        raise Exception(f"Broker request failed after {retries} retries.")
