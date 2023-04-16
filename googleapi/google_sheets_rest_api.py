import google.auth
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache


def get_google_sheets_api_service():
    class MemoryCache(Cache):
        _CACHE = {}

        def get(self, url):
            return MemoryCache._CACHE.get(url)

        def set(self, url, content):
            MemoryCache._CACHE[url] = content

    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive.file"]  # TODO: mayby add dumping attached file into the current google drive folder
    credentials, project_id = google.auth.default(scopes)
    service = build('sheets', 'v4', credentials=credentials, cache=MemoryCache())
    return service
