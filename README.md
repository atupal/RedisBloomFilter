RedisBloomFilter
================

A bloom filter use redis as backend , writed with Python

Use code from https://github.com/jaybaird/python-bloomfilter
See the LICENSE

```python
>>> from redisfilter import RedisBloomFilter
>>> f = RedisBloomFilter(capacity=1000, error_rate=0.001)
>>> [f.add(x) for x in range(10)]
>>> all([(x in f) for x in range(10)])
True
>>> 10 in f
False
>>> 5 in f
True
>>> f = RedisBloomFilter(capacity=1000, error_rate=0.001)
>>> for i in xrange(0, f.capacity):
...     f.add(i)
>>> (1.0 - (len(f) / float(f.capacity))) <= f.error_rate + 2e-18
True
```
