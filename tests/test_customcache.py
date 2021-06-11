import unittest
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


class CustomTTLCacheTest(unittest.TestCase):

    Cache = CustomTTLTestCache

    def test_ttl(self):
        cache = CustomTTLCache(2, 1, 'REJECT', timer=Timer())
        self.assertEqual(0, cache.timer())
        self.assertEqual(1, cache.ttl)

        cache[1] = 1
        self.assertEqual({1}, set(cache))
        self.assertEqual(1, len(cache))
        self.assertEqual(1, cache[1])

        cache.timer.tick()
        self.assertEqual({1}, set(cache))
        self.assertEqual(1, len(cache))
        self.assertEqual(1, cache[1])
        cache[2] = 2
        self.assertEqual({1, 2}, set(cache))
        self.assertEqual(2, len(cache))
        self.assertEqual(1, cache[1])
        self.assertEqual(2, cache[2])

        cache.timer.tick()
        self.assertEqual({2}, set(cache))
        self.assertEqual(1, len(cache))
        self.assertNotIn(1, cache)
        self.assertEqual(2, cache[2])

        cache[3] = 3
        self.assertEqual({2, 3}, set(cache))
        self.assertEqual(2, len(cache))
        self.assertNotIn(1, cache)
        self.assertEqual(2, cache[2])
        self.assertEqual(3, cache[3])

        cache.timer.tick()
        self.assertEqual({3}, set(cache))
        self.assertEqual(1, len(cache))
        self.assertNotIn(1, cache)
        self.assertNotIn(2, cache)
        self.assertEqual(3, cache[3])

        cache.timer.tick()
        self.assertEqual(set(), set(cache))
        self.assertEqual(0, len(cache))
        self.assertNotIn(1, cache)
        self.assertNotIn(2, cache)
        self.assertNotIn(3, cache)

        with self.assertRaises(KeyError):
            del cache[1]

    def test_ttl_expire(self):
        cache = CustomTTLCache(3, 2, 'REJECT', timer=Timer())
        with cache.timer as time:
            self.assertEqual(time, cache.timer())
        self.assertEqual(2, cache.ttl)

        cache[1] = 1
        cache.timer.tick()
        cache[2] = 2
        cache.timer.tick()
        cache[3] = 3
        self.assertEqual(2, cache.timer())

        self.assertEqual({1, 2, 3}, set(cache))
        self.assertEqual(3, len(cache))
        self.assertEqual(1, cache[1])
        self.assertEqual(2, cache[2])
        self.assertEqual(3, cache[3])

        cache.expire()
        self.assertEqual({1, 2, 3}, set(cache))
        self.assertEqual(3, len(cache))
        self.assertEqual(1, cache[1])
        self.assertEqual(2, cache[2])
        self.assertEqual(3, cache[3])

        cache.expire(3)
        self.assertEqual({2, 3}, set(cache))
        self.assertEqual(2, len(cache))
        self.assertNotIn(1, cache)
        self.assertEqual(2, cache[2])
        self.assertEqual(3, cache[3])

        cache.expire(4)
        self.assertEqual({3}, set(cache))
        self.assertEqual(1, len(cache))
        self.assertNotIn(1, cache)
        self.assertNotIn(2, cache)
        self.assertEqual(3, cache[3])

        cache.expire(5)
        self.assertEqual(set(), set(cache))
        self.assertEqual(0, len(cache))
        self.assertNotIn(1, cache)
        self.assertNotIn(2, cache)
        self.assertNotIn(3, cache)

    def test_ttl_atomic(self):
        cache = CustomTTLCache(1, 1, 'REJECT', timer=Timer(auto=True))
        cache[1] = 1
        self.assertEqual(1, cache[1])
        cache[1] = 1
        self.assertEqual(1, cache.get(1))
        cache[1] = 1
        self.assertEqual(1, cache.pop(1))
        cache[1] = 1
        self.assertEqual(1, cache.setdefault(1))
        cache[1] = 1
        cache.clear()
        self.assertEqual(0, len(cache))

    def test_ttl_tuple_key(self):
        cache = CustomTTLCache(1, 0, 'REJECT', timer=Timer())
        self.assertEqual(0, cache.ttl)

        cache[(1, 2, 3)] = 42
        self.assertEqual(42, cache[(1, 2, 3)])
        cache.timer.tick()
        with self.assertRaises(KeyError):
            cache[(1, 2, 3)]
        self.assertNotIn((1, 2, 3), cache)


if __name__ == '__main__':
    unittest.main()
