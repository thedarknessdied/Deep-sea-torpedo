import re
from utils.default import HTTP_REQUEST_PROTOCOL
from utils.default import HTTP_REQUEST_DATA_TYPE


class WebRequestsData(object):
    """

        package =>
        {
            'line': {
                'method': 'get',
                'path': '/',
                'version': 'http/1.1'
            },
            'header': {
                'host': 'www.baidu.com',
                'user-agent': 'mozilla/5.0 (windows nt 10.0; win64; x64; rv:109.0) gecko/20100101 firefox/119.0',
                'connection': 'close'
            },
            'data': '',
            'protocol': 'https',
            'data_type': 'data'
        }
    """
    HTTP_REQUEST_PROTOCOL = HTTP_REQUEST_PROTOCOL
    HTTP_REQUEST_DATA_TYPE = HTTP_REQUEST_DATA_TYPE
    # 构建HTTP请求package的参数名称
    HEADER_LINE_PARAM_NAME = ['method', 'path', 'version']

    def __init__(self, protocol: str = 'http', data_type: str = 'data', mode: str = 'stream', **kwargs):
        from utils.utils import get_str_from_dict
        self.is_usable = True
        self.protocol = protocol
        self.data_type = data_type
        self.mode = mode

        if self.mode == 'stream':
            content = get_str_from_dict('content', kwargs, str, "")
            self.package = self._parse_html_request(content)
            self._check_requests_package()
        else:
            ''' 将字典转化为清河报文(组合) '''
            self.method = get_str_from_dict('method', kwargs, str, "get")
            self.path = get_str_from_dict('path', kwargs, str, "/")
            self.version = get_str_from_dict('version', kwargs, str, "")
            self.headers = get_str_from_dict('headers', kwargs, str, "")
            self.host = get_str_from_dict('host', kwargs, str, "")
            self.data = get_str_from_dict('data', kwargs, any, None)
            self.package = self._combine_param()
            self._check_requests_package()

    @classmethod
    def _get_requests_header_line_mode(cls) -> re.Pattern:
        """
            获取请求行验证的模板
            HTTP 请求行必须严格按照 protocol path?search_param#fragment version
        :return: 请求行验证模板
        """
        return re.compile("^(?P<method>(GET|POST))\s+(?P<path>(\S*))\s+(?P<version>(.*))", re.I)

    def _get_requests_header_line_param(self, content) -> re.Match:
        """
            校验传入的请求行是否符合要求，符合要求则将is_usable设置为True，否则设置为False
        :param content: 请求行数据
        :return:
        """
        _mode = self._get_requests_header_line_mode()
        groups = _mode.search(content)
        if groups is None or not groups:
            self.is_usable = False
        else:
            self.is_usable = True
        return groups

    def _parse_request_line_header(self, content: str) -> dict:
        """
            解析请求行content中的内容是否符合HTTP报文的格式
        :param content:请求行content
        :return:
        """
        content = content.strip(" ")
        groups = self._get_requests_header_line_param(content)
        if groups is None:
            return dict()

        request_header_result = {
            'method': None,
            'path': None,
            'version': None
        }
        _res = list()
        for item in self.HEADER_LINE_PARAM_NAME:
            request_header_result[item] = groups.group(item).strip().lower()
        return request_header_result

    @classmethod
    def _get_requests_header_headers_mode(cls) -> re.Pattern:
        """
            获取请求头数据分离的模板
        :return: 请求头数据分离的模板
        """
        return re.compile("(?P<key>(\S*?)):(?P<value>(.*))", re.I)

    @classmethod
    def _parse_request_headers_header(cls, mode: re.Pattern, content: str) -> (str, str):
        """
            通过请求头数据分离模板将请求头数据mode的键值对分离
        :param mode: 请求头数据分离模板
        :param content: 请求头数据
        :return:
        """
        groups = mode.search(content)
        if groups is None:
            return "", None
        return groups.group("key").strip().lower(), groups.group("value").strip().lower()

    def _parse_html_request(self, content: str) -> dict:
        """
            将HTTP Request报文解析成由请求行、请求头、请求体组成的字典
        :param content: HTTP Request报文
        :return:
        """
        lines = content.splitlines()

        ''' 清除报文前的空行 '''
        _index = 0
        length = len(lines)
        while _index < length and not lines[_index].strip(" "):
            _index = _index + 1
        if _index >= length:
            self.is_usable = False
            return dict()

        lines = lines[_index:]
        ''' 协议报文的第一行是请求行 '''
        request_header_line = lines[0]
        _requests_line = self._parse_request_line_header(request_header_line)
        if not isinstance(_requests_line, dict) or not _requests_line:
            self.is_usable = False
            return dict()

        ''' 协议报文第二行开始到最近的一个非空行为止为请求头 '''
        _requests_headers = dict()
        # 记录属于请求头的行数
        index = 1
        _requests_headers_line = lines[1:]
        _requests_headers__line_mode = self._get_requests_header_headers_mode()
        for item in _requests_headers_line:
            _item = item.strip()
            if not _item:
                break
            _header_item_key, _header_item_value = self._parse_request_headers_header(_requests_headers__line_mode,
                                                                                      _item)
            if _header_item_key:
                if _requests_headers.get(_header_item_key, None):
                    _requests_headers.setdefault(_header_item_key, _header_item_value)
                else:
                    _requests_headers[_header_item_key] = _header_item_value
            index = index + 1
        if not isinstance(_requests_headers, dict) or not _requests_headers:
            self.is_usable = False
            return dict()
        if _requests_headers.get("host", None) is None:
            self.is_usable = False
            return dict()

        ''' 剩下的都属于请求体的数据 '''
        try:
            _requests_data = lines[index + 1:]
        except IndexError:
            self.is_usable = True
            return {
                'line': _requests_line,
                'header': _requests_headers,
                'data': ''
            }
        _requests_data = "\r\n".join(_requests_data)
        self.is_usable = True
        return {
            'line': _requests_line,
            'header': _requests_headers,
            'data': _requests_data,
            'protocol': self.protocol,
            'data_type': self.data_type
        }

    def _check_requests_package(self):
        """
            校验基础的HTTP请求内容是否完整
        :return:
        """
        if self.is_usable:
            line = self.package.get('line', dict())
            header = self.package.get('header', dict())
            if not line or not isinstance(line, dict) or not header or not isinstance(header, dict):
                self.is_usable = False
                return
            line_method = line.get('method', '')
            path = line.get('path', '')
            version = line.get('version', '')
            if not line_method or not isinstance(line_method, str) or not path \
                    or not isinstance(path,  str) or not version or not isinstance(version, str):
                self.is_usable = False
                return
            if line_method not in self.HTTP_REQUEST_PROTOCOL:
                self.is_usable = False
                return
            host = header.get('host', '')
            if not host or not isinstance(host, str):
                self.is_usable = False
                return
            if self.data_type not in self.HTTP_REQUEST_DATA_TYPE:
                self.is_usable = False
                return

    def _combine_param(self) -> dict:
        """
            通过字典传入的参数进行web包的构建
        :return:
        """
        if self.headers.get('host', None) is None:
            self.is_usable = False
            self.host = None
        else:
            self.host = self.headers.get('host', None)
        package = {
            'line': {
                'method': self.method,
                'path': self.path,
                'version': self.version
            },
            'headers': self.headers,
            'data': self.data,
            'protocol': self.protocol,
            'data_type': self.data_type
        }
        return package
