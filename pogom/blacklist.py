#!/usr/bin/python
# -*- coding: utf-8 -*-


# Global IP blacklist.
def get_blacklist():
    try:
        url = 'https://blist.devkat.org/blacklist.json'
        blacklist = requests.get(url, timeout=5).json()
        log.debug('Entries in blacklist: %s.', len(blacklist))
        return blacklist
    except (requests.exceptions.RequestException, IndexError, KeyError):
        log.error('Unable to retrieve blacklist, setting to empty.')
        return []


# Fingerprinting methods. They receive Flask's request object as
# argument.

# No referrer = request w/o being on a website.
def _no_referrer(request):
    return not request.referrer


# iPokeGo.
def _iPokeGo(request):
    if not request.referrer:
        return False

    return 'ipokego' in request.referrer.lower()


# Prepare blacklisted fingerprints. A list of functions that
# return True when the fingerprint matches. The function
# receives Flask's request object as argument.
fingerprints = [
    _no_referrer,
    _iPokeGo
]
