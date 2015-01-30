"""Simple Python client for represent.opennorth.ca."""

from __future__ import with_statement

import logging
from datetime import datetime, timedelta
from itertools import dropwhile
from threading import Lock
from time import sleep

import requests

BASE_URL = 'https://represent.opennorth.ca'

log = logging.getLogger(__name__)

rate_limit_period = 60  # Period to watch for.
rate_limit = 60         # How many per period.
rate_history = []
rate_lock = Lock()


def limit_rate():
    """Ensure we're not going too fast (under 60 times a minute)."""
    global rate_history

    with rate_lock:
        now = datetime.utcnow()
        a_min_ago = now - timedelta(seconds=rate_limit_period)
        rate_history = list(dropwhile(lambda x: x < a_min_ago, rate_history))

        if len(rate_history) >= rate_limit:
            log.debug('Throttling opennorth API calls')
            sleep(rate_limit_period - (now - rate_history[0]).total_seconds())

        rate_history.append(datetime.utcnow())


def get(path, throttle=True, **params):
    """Return a JSON-decoded object from the provided API path.
    
    :param path: the target API path.
    :param throttle: whether we should rate-limit requests to 60/minute max.
    :param params: query string parameters passed to the API.

    """
    log.debug('Fetching %r %r' % (path, params))

    if throttle:
        limit_rate()

    response = requests.get(''.join([BASE_URL, path]), params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_all(path, **params):
    """Iterate through all result pages.
    
    :param path: the target API path.
    :param params: query string parameters passed to the API.

    """
    while True:
        results = get(path, **params)
        for result in results.get('objects'):
            yield result

        path = results.get('meta', dict()).get('next')
        if not path:
            break


def boundary_set(name=None, **params):
    """Return one or more boundary sets.
    
    :param name: the wanted boundary set.

    See http://represent.opennorth.ca/api/#boundaryset
    
    """
    path = '/boundary-sets'
    if name:
        path = '/'.join([path, name])
        return get('%s/' % path, **params)
    return get_all('%s/' % path, **params)


def boundary(boundary_set=None, name=None, representatives=False, **params):
    """Return one or more boundary or its representatives.
    
    :param boundary_set: the wanted boundary set.
    :param name: the name of the boundary.
    :param representatives: whether or not to return the representatives for
        the boundary instead.

    See http://represent.opennorth.ca/api/#boundary
    
    """
    path = '/boundaries'
    if boundary_set:
        path = '/'.join([path, boundary_set])
        if name:
            path = '/'.join([path, name])
            if not representatives:
                return get('%s/' % path, **params)
            path = '/'.join([path, 'representatives'])
    return get_all('%s/' % path, **params)


def postcode(code=None):
    """Return boundary info for a postal code.
    
    See http://represent.opennorth.ca/api/#postcode
    
    """
    path = '/postcodes'
    if code:
        path = '/'.join([path, code])
    return get('%s/' % path)


def representative_set(repr_set=None):
    """Return one or more representative set.

    :param repr_set: the wanted representative set.

    See http://represent.opennorth.ca/api/#representativeset

    """
    path = '/representative-sets'
    if repr_set:
        path = '/'.join([path, repr_set])
        return get('%s/' % path)
    return get_all('%s/' % path)


def representative(repr_set=None, **params):
    """Return all members from the specified representative set, if any.

    :param repr_set: the wanted representative set.

    See http://represent.opennorth.ca/api/#representative

    """
    path = '/representatives'
    if repr_set:
        path = '/'.join([path, repr_set])
    return get_all('%s/' % path, **params)
