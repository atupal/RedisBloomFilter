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

**Note: Don't forgot clear the redis bitkey before you use the filter ;)**
e.g.
```python
scalablef = ScalableRedisBloomFilter(initial_capacity=100, error_rate=0.001, prefixbitkey='hehe', clear_filter=True)
f = RedisBloomFilter(1000, error_rate=0.001, bitkey='haha', clear_filter=True)
keys_in = []
keys_notin = []
from uuid import uuid4
for i in range_fn(500):
    keys_in.append(str(uuid4()))
for i in range_fn(500):
    keys_notin.append(str(uuid4()))

for key in keys_in:
    scalablef.add(key)
    f.add(key)

print ([ key in scalablef for key in keys_in ])
print ([ key in scalablef for key in keys_notin ])
print ([ key in f for key in keys_in ])
print (([ key in f for key in keys_notin ]))
```
