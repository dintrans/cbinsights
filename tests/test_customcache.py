import pytest
from src.CustomTtlCache import CustomTTLCache


class Timer:
    def __init__(self, auto=False):
        self.auto = auto
        self.time = 0

    def __call__(self):
        if self.auto:
            self.time += 1
        return self.time

    def tick(self):
        self.time += 1


class CustomTTLTestCache(CustomTTLCache):
    def __init__(self, maxsize, default_ttl, eviction_policy, **kwargs):
        CustomTTLCache.__init__(self, maxsize, default_ttl, eviction_policy, timer=Timer(), **kwargs)


Cache = CustomTTLTestCache


def test_ttl():
    cache = CustomTTLCache(2, 1, 'REJECT', timer=Timer())
    assert 0 == cache.timer()
    assert 1 == cache.ttl

    cache[1] = 1
    assert {1} == set(cache)
    assert 1 == len(cache)
    assert 1 == cache[1]

    cache.timer.tick()
    assert {1} == set(cache)
    assert 1 == len(cache)
    assert 1 == cache[1]
    cache[2] = 2
    assert {1, 2} == set(cache)
    assert 2 == len(cache)
    assert 1 == cache[1]
    assert 2 == cache[2]

    cache.timer.tick()
    assert {2} == set(cache)
    assert 1, len(cache)
    assert 1 not in cache
    assert 2 == cache[2]

    cache[3] = 3
    assert {2, 3} == set(cache)
    assert 2 == len(cache)
    assert 1 not in cache
    assert 2 == cache[2]
    assert 3 == cache[3]

    cache.timer.tick()
    assert {3} == set(cache)
    assert 1 == len(cache)
    assert 1 not in cache
    assert 2 not in cache
    assert 3 == cache[3]

    cache.timer.tick()
    assert set() == set(cache)
    assert 0 == len(cache)
    assert 1 not in cache
    assert 2 not in cache
    assert 3 not in cache

    with pytest.raises(KeyError):
        del cache[1]


def test_ttl_expire():
    cache = CustomTTLCache(3, 2, 'REJECT', timer=Timer())
    with cache.timer as time:
        assert time == cache.timer()
    assert 2 == cache.ttl

    cache[1] = 1
    cache.timer.tick()
    cache[2] = 2
    cache.timer.tick()
    cache[3] = 3
    assert 2 == cache.timer()

    assert {1, 2, 3} == set(cache)
    assert 3 == len(cache)
    assert 1 == cache[1]
    assert 2 == cache[2]
    assert 3 == cache[3]

    cache.expire()
    assert {1, 2, 3} == set(cache)
    assert 3, len(cache)
    assert 1 == cache[1]
    assert 2 == cache[2]
    assert 3 == cache[3]

    cache.expire(3)
    assert {2, 3} == set(cache)
    assert 2 == len(cache)
    assert 1 not in cache
    assert 2 == cache[2]
    assert 3 == cache[3]

    cache.expire(4)
    assert {3} == set(cache)
    assert 1 == len(cache)
    assert 1 not in cache
    assert 2 not in cache
    assert 3 == cache[3]

    cache.expire(5)
    assert set() == set(cache)
    assert 0 == len(cache)
    assert 1 not in cache
    assert 2 not in cache
    assert 3 not in cache


def test_ttl_atomic():
    cache = CustomTTLCache(1, 1, 'REJECT', timer=Timer(auto=True))
    cache[1] = 1
    assert 1 == cache[1]
    cache[1] = 1
    assert 1 == cache.get(1)
    cache[1] = 1
    assert 1 == cache.pop(1)
    cache[1] = 1
    assert 1 == cache.setdefault(1)
    cache[1] = 1
    cache.clear()
    assert 0 == len(cache)


def test_ttl_tuple_key():
    cache = CustomTTLCache(1, 0, 'REJECT', timer=Timer())
    assert 0 == cache.ttl

    cache[(1, 2, 3)] = 42
    assert 42 == cache[(1, 2, 3)]
    cache.timer.tick()
    with pytest.raises(KeyError):
        cache[(1, 2, 3)]
    assert (1, 2, 3) not in cache


def test_reject_policy():
    cache = CustomTTLCache(3, 1, 'REJECT', timer=Timer())

    cache[1] = 1
    cache[2] = 2
    cache[3] = 3

    assert {1, 2, 3} == set(cache)
    with pytest.raises(KeyError):
        cache[4] = 44
    assert 1 == cache[1]
    assert 2 == cache[2]
    assert 3 == cache[3]


def test_fifo_policy():
    cache = CustomTTLCache(3, 5, 'FIFO', timer=Timer())

    cache[1] = 1
    cache.timer.tick()
    cache[2] = 2
    cache.timer.tick()
    cache[3] = 3
    cache.timer.tick()
    assert {1, 2, 3} == set(cache)

    cache[4] = 4

    assert {2, 3, 4} == set(cache)
    assert 1 not in cache
    assert 2 == cache[2]
    assert 3 == cache[3]
    assert 4 == cache[4]


def test_lifo_policy():
    cache = CustomTTLCache(3, 5, 'LIFO', timer=Timer())

    cache[1] = 1
    cache.timer.tick()
    cache[2] = 2
    cache.timer.tick()
    cache[3] = 3
    cache.timer.tick()
    assert {1, 2, 3} == set(cache)

    cache[4] = 4

    assert {1, 2, 4} == set(cache)
    assert 3 not in cache
    assert 1 == cache[1]
    assert 2 == cache[2]
    assert 4 == cache[4]


def test_replace_edgecase():
    cache = CustomTTLCache(3, 5, 'REJECT', timer=Timer())

    cache[1] = 11
    cache.timer.tick()
    cache[2] = 22
    cache.timer.tick()
    cache[3] = 33
    cache.timer.tick()
    assert {1, 2, 3} == set(cache)

    cache[1] = 44

    assert {1, 2, 3} == set(cache)
    assert 44 == cache[1]
    assert 22 == cache[2]
    assert 33 == cache[3]
