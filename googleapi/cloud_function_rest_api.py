import socket

import google.auth
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache


def get_cloud_function_api_service():
    class MemoryCache(Cache):
        _CACHE = {}

        def get(self, url):
            return MemoryCache._CACHE.get(url)

        def set(self, url, content):
            MemoryCache._CACHE[url] = content

    scopes = ['https://www.googleapis.com/auth/cloud-platform']

    credentials, project_id = google.auth.default(scopes)

    # Fix for issue: socket.timeout: The read operation timed out
    # Solution from: https://github.com/googleapis/google-api-python-client/issues/632#issuecomment-541973021
    socket.setdefaulttimeout(300)

    service = build('cloudfunctions', 'v1', credentials=credentials, cache=MemoryCache())
    return service
