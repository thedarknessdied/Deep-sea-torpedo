from core.ProcessRequestData import WebRequestsData
import requests
import urllib3
from core.ProcessProxy import WebProxy

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WebRequest(object):
    def __init__(self, proxies: None or WebProxy = None, *args, **kwargs):
        self.proxies = proxies.show_proxy() if isinstance(proxies, WebProxy) else None
        self.data = WebRequestsData(**kwargs)
        if self.data.is_usable:
            self.session = requests.session()
        else:
            self.session = None

    def make_request(self) -> (bool, str or requests.models.Response):
        if self.session and isinstance(self.session, requests.Session):
            url = f"{self.data.package['protocol']}://{self.data.package['header']['host']}/{self.data.package['line']['path']}"
            data_type = self.data.package['data_type']
            data = self.data.package['data']
            if data_type == 'data':
                try:
                    res = self.session.request(method=self.data.package['line']['method'], url=url,
                                               headers=self.data.package['header'], allow_redirects=True,
                                               data=data, proxies=self.proxies, verify=False)
                    return True, res
                except Exception as e:
                    return False, "发生异常错误"
            elif data_type == 'json':
                try:
                    res = self.session.request(method=self.data.package['line']['method'], url=url,
                                               headers=self.data.package['header'], allow_redirects=True,
                                               json=data, proxies=self.proxies, verify=False)
                    return True, res
                except Exception as e:
                    return False, "发生异常错误"
            elif data_type == 'files':
                try:
                    res = self.session.request(method=self.data.package['line']['method'], url=url,
                                               headers=self.data.package['header'], allow_redirects=True,
                                               files=data, proxies=self.proxies, verify=False)
                    return True, res
                except Exception as e:
                    return False, "发生异常错误"
            else:
                return False, "发生异常错误"
        else:
            return False, "发生异常错误"

    def make_response(self, charset="UTF-8") -> (bool, str):
        status, res = self.make_request()
        if not status or not isinstance(res, requests.models.Response):
            return False, ""
        headers = res.headers
        _headers = list()
        url = res.url
        status_code = res.status_code
        content = res.content.decode(res.encoding if res.encoding is not None else charset)
        for k, v in headers.items():
            _headers.append(f"{k}:{v}")
        headers = "\r\n".join(_headers)
        result = f"{self.data.package['line']['version']} {url} {status_code}\r\n{headers}\r\n\r\n{content}"
        return True, result
