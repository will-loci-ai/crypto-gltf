import os
from urllib.parse import unquote


def uri_to_path(uri):
    uri = uri.replace("\\", "/")  # Some files come with \\ as dir separator
    uri = unquote(uri)
    return os.path.normpath(uri)
