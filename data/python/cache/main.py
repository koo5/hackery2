from diskcache import Cache

cache = Cache('rates', timeout=None, expire=None, eviction_policy='none')

@cache.memoize()
def get_rates(date: str):
	return {'USB':date[0], 'USD':date[1], 'USA':1.0}

lock = Lock(cache, 'report-123')

