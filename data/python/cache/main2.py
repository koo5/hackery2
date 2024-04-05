import diskcache, time
from diskcache import barrier, Lock, Cache

cache = diskcache.Cache('cache')


def get_rates(date):
	date += 300
	rate = cache.get(date)
	if rate is not None:
		return rate
	return get_rates2(date)
	

@diskcache.barrier(cache, diskcache.Lock)
def get_rates2(date):
	
	rate = cache.get(date)
	
	if rate is not None:
		return rate
	
	print('started', date)
	time.sleep(1)
	result = date * 100
	print('finished', date)
	
	cache.set(date, result)
	
	return result 

import multiprocessing.pool

pool = multiprocessing.pool.ThreadPool(2)

print(pool.map(get_rates, [1, 1, 3, 4, 5, 5, 5, 8, 9, 10])) 
