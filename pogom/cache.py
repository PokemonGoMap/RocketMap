#!/usr/bin/python
# -*- coding: utf-8 -*-

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': 'cache/data',
    'cache.lock_dir': 'cache/lock'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))
