import os

REDIS_HOST = os.environ.get('REDIS_HOST') or '127.0.0.1'
REDIS_PORT = int(os.environ.get('REDIS_HOST') or 6379)
STREAM_KEYS = (os.environ.get('STREAM_KEYS', 'trades/BTCUSDT,orders/BTCUSDT')).split(',')
