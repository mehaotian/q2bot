from urllib.parse import urlparse, urlunparse, urlencode
# from .hkey.plain import calculate as plain
# from .hkey.web import calculate as web
from android import calculate as android

HeyboxURLPrefix = 'https://api.xiaoheihe.cn'

class InvalidUrlError(Exception):
    pass

def calculate(url, timestamp=0, nonce='', algorithm=None):
    """
    Calculate the hkey for the given Heybox API URL.

    :param url: Heybox API URL.
    :param timestamp: Optional timestamp to customize the hkey algorithm.
    :param nonce: Optional nonce to customize the hkey algorithm.
    :param algorithm: Optional algorithm type to use ('web', 'android', or default to 'plain').
    :return: URL with hkey query appended.
    :raises InvalidUrlError: If the URL does not start with the Heybox prefix.
    """
    if not url.startswith(HeyboxURLPrefix):
        raise InvalidUrlError(f"Not a Heybox URL: {url}")

    query = android(url, timestamp, nonce)
    # Determine which algorithm to use
    # if algorithm == 'web':
    #     query = web(url, timestamp, nonce)
    # elif algorithm == 'android':
    #     query = android(url, timestamp, nonce)
    # else:
    #     query = plain(url, timestamp, nonce)

    # Parse the URL and append the hkey query
    parsed_url = urlparse(url)
    query_string = parsed_url.query
    if query_string:
        query_string += '&' + query
    else:
        query_string = query

    # Rebuild the URL with the updated query string
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        query_string,
        parsed_url.fragment
    ))

    return new_url


url = calculate('https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&userid=1985029&limit=20&offset=0&post_type=2&list_type=article')
print(url)