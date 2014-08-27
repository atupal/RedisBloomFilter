# -*- coding: utf-8 -*-
"""
    filter.py
    ~~~~~~~~~
"""

from __future__ import absolute_import
import math
import sys
try:
    import StringIO
    import cStringIO
except ImportError:
    from io import BytesIO
import hashlib
from struct import unpack, pack, calcsize

running_python_3 = sys.version_info[0] == 3

def range_fn(*args):
    if running_python_3:
        return range(*args)
    else:
        return xrange(*args)


def is_string_io(instance):
    if running_python_3:
       return isinstance(instance, BytesIO)
    else:
        return isinstance(instance, (StringIO.StringIO,
                                     cStringIO.InputType,
                                     cStringIO.OutputType))

def make_hashfuncs(num_slices, num_bits):
    if num_bits >= (1 << 31):
        fmt_code, chunk_size = 'Q', 8
    elif num_bits >= (1 << 15):
        fmt_code, chunk_size = 'I', 4
    else:
        fmt_code, chunk_size = 'H', 2
    total_hash_bits = 8 * num_slices * chunk_size
    if total_hash_bits > 384:
        hashfn = hashlib.sha512
    elif total_hash_bits > 256:
        hashfn = hashlib.sha384
    elif total_hash_bits > 160:
        hashfn = hashlib.sha256
    elif total_hash_bits > 128:
        hashfn = hashlib.sha1
    else:
        hashfn = hashlib.md5
    fmt = fmt_code * (hashfn().digest_size // chunk_size)
    num_salts, extra = divmod(num_slices, len(fmt))
    if extra:
        num_salts += 1
    salts = tuple(hashfn(hashfn(pack('I', i)).digest()) for i in range_fn(num_salts))
    def _make_hashfuncs(key):
        if running_python_3:
            if isinstance(key, str):
                key = key.encode('utf-8')
            else:
                key = str(key).encode('utf-8')
        else:
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            else:
                key = str(key)
        i = 0
        for salt in salts:
            h = salt.copy()
            h.update(key)
            for uint in unpack(fmt, h.digest()):
                yield uint % num_bits
                i += 1
                if i >= num_slices:
                    return

    return _make_hashfuncs

class RedisBloomFilter(object):

    def __init__(self, capacity, error_rate=0.001,
                       connection=None, 
                       bitkey='bloom_filter', clear_filter=False):
        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")
        if not capacity > 0:
            raise ValueError("Capacity must be > 0")
        self.capacity = capacity
        self.error_rate = error_rate

        self.connection = connection
        if not self.connection:
            import redis
            self.connection = redis.Redis()
        self.bitkey = bitkey
        if clear_filter:
            self.connection.delete(self.bitkey)

        num_slices = int(math.ceil(math.log(1.0 / error_rate, 2)))
        bits_per_slice = int(math.ceil(
            (capacity * abs(math.log(error_rate))) /
            (num_slices * (math.log(2) ** 2))))
        self._setup(error_rate, num_slices, bits_per_slice, capacity, 0)

    def _setup(self, error_rate, num_slices, bits_per_slice, capacity, count):
        self.error_rate = error_rate
        self.num_slices = num_slices
        self.bits_per_slice = bits_per_slice
        self.capacity = capacity
        self.num_bits = num_slices * bits_per_slice
        self.count = count
        self.make_hashes = make_hashfuncs(self.num_slices, self.bits_per_slice)

    def __contains__(self, key):
        """Tests a key's membership in this bloom filter.

        >>> b = BloomFilter(capacity=100)
        >>> b.add("hello")
        False
        >>> "hello" in b
        True

        """
        bits_per_slice = self.bits_per_slice
        pipeline = self.connection.pipeline(transaction=False)
        hashes = self.make_hashes(key)
        offset = 0
        for k in hashes:
            pipeline.getbit(self.bitkey, offset+k)
            offset += bits_per_slice
        results = pipeline.execute()
        return all(results)

    def __len__(self):
        """Return the number of keys stored by this bloom filter."""
        return self.count

    def add(self, key):
        """ Adds a key to this bloom filter. If the key already exists in this
        filter it will return True. Otherwise False.

        >>> b = BloomFilter(capacity=100)
        >>> b.add("hello")
        False
        >>> b.add("hello")
        True
        >>> b.count
        1

        """
        pipeline = self.connection.pipeline(transaction=False)
        bits_per_slice = self.bits_per_slice
        hashes = self.make_hashes(key)
        found_all_bits = True
        if self.count > self.capacity:
            raise IndexError("BloomFilter is at capacity")
        offset = 0
        for k in hashes:
            pipeline.setbit(self.bitkey, offset + k, 1)
            offset += bits_per_slice
        pipeline.execute()

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['make_hashes']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.make_hashes = make_hashfuncs(self.num_slices, self.bits_per_slice)

def test():
    f = RedisBloomFilter(capacity=1000, error_rate=0.001)
    for i in range_fn(0, f.capacity):
        f.add(i)

    print (0 in f)

if __name__ == '__main__':
    test()
