import collections
import time

from cachetools.cache import Cache
from cachetools import TTLCache
from cachetools.ttl import _Link, _Timer


class CustomTTLCache(TTLCache):
    """Cache implementation with per-item TTL value,
    support for FIFO, LIFO and Reject eviction policies."""

    eviction_policy_options = {
        'FIFO': lambda n: Cache.__delitem__(n, n._TTLCache__root.next.key),
        'LIFO': lambda n: Cache.__delitem__(n, n._TTLCache__root.prev.key),
        'Reject': lambda _: (_ for _ in ()).throw(ValueError)  # hackySolution
    }

    def __init__(self, maxsize, default_ttl, evctn_plc, timer=time.monotonic):
        self.__eviction_policy = evctn_plc
        super().__init__(maxsize, default_ttl, timer=timer, getsizeof=None)

    def __setitem__(self, key, value, ttl=-1, cache_setitem=Cache.__setitem__):
        if self.currsize >= (self.maxsize):
            self.eviction_policy_options[self.__eviction_policy](self)
        with self._TTLCache__timer as time:
            self.expire(time)
            cache_setitem(self, key, value)
        try:
            link = self._TTLCache__getlink(key)
        except KeyError:
            self._TTLCache__links[key] = link = _Link(key)
        else:
            link.unlink()
        if ttl == 0:
            ttl = sys.maxsize
        elif ttl <= -1:
            ttl = self._TTLCache__ttl
        link.expire = time + ttl
        link.next = root = self._TTLCache__root
        link.prev = prev = root.prev
        prev.next = root.prev = link

    def expire(self, time=None):
        """Remove expired items from the cache."""
        if time is None:
            time = self._TTLCache__timer()
        root = self._TTLCache__root
        curr = root.next
        links = self._TTLCache__links
        cache_delitem = Cache.__delitem__
        while curr is not root:
            next = curr.next
            if curr.expire < time:
                cache_delitem(self, curr.key)
                del links[curr.key]
                curr.unlink()
            curr = next