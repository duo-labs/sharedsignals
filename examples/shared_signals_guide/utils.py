# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import contextlib
import warnings

import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util import connection

old_merge_environment_settings = requests.Session.merge_environment_settings
old_create_connection = connection.create_connection


def patch_hosts(host_to_ip):
    """Provides mapping from host address to IP prior to making a request."""

    def patched_create_connection(address, *args, **kwargs):
        host, port = address
        if host in host_to_ip:
            host = host_to_ip[host]

        return old_create_connection((host, port), *args, **kwargs)

    connection.create_connection = patched_create_connection


@contextlib.contextmanager
def no_ssl_verification():
    """
    Default verify=False for all request calls for simplicity in this demo.
    Do not do this in production!
    From https://stackoverflow.com/questions/15445981/how-do-i-disable-the-security-certificate-check-in-python-requests
    """
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass
