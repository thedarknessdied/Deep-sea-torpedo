STATIC_FOLDER = "static"
TEMPLATES_FOLDER = "templates"

DEFAULT_WEB_PROXY = {
    'status': False,
    'type': None,
    "value": None
}
DEFAULT_PROXY = {
    'web_proxy': DEFAULT_WEB_PROXY,
    'system_proxy': {
        'status': False,
        "valuevalue": None
    }
}

# web端请求数据使用代理时允许使用的代理协议类型
HTTP_REQUEST_PROXY_PROTOCOL = ["http", "https", "socks4", "socks5", "all"]
# web端请求数据使用代理时建立的代理池最大数量
HTTP_REQUEST_PROXY_POOL_MAX_SIZE = 10
# web端请求数据使用代理时建立的代理池最小数量
HTTP_REQUEST_PROXY_POOL_MIN_SIZE = 1
# web端请求数据允许使用的协议
HTTP_REQUEST_PROTOCOL = ['get', 'post', 'put', 'option']
# web端请求数据允许传递的数据类型
HTTP_REQUEST_DATA_TYPE = ['data', 'json', 'files']
