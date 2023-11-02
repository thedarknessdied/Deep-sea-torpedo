import re


class WebProxy(object):
    from utils.default import HTTP_REQUEST_PROXY_PROTOCOL
    # web端请求数据使用代理时允许使用的代理协议类型
    HTTP_REQUEST_PROXY_PROTOCOL = HTTP_REQUEST_PROXY_PROTOCOL
    # 构建代理 URL 所需要的参数名称
    PARAM_NAME = ['protocol', 'authorize', 'hostname', 'port']

    def __init__(self, *args, **kwargs):
        self.is_usable = False
        if args is None or not args:
            ''' 将字典转化为代理IP字符串(组合) '''
            self.protocol = self._get_str_from_dict('protocol', kwargs, str, "")
            self.hostname = self._get_str_from_dict('hostname', kwargs, str, "")
            self.port = self._get_str_from_dict('port', kwargs, str, "")
            self.username = self._get_str_from_dict('username', kwargs, str, "")
            self.password = self._get_str_from_dict('password', kwargs, str, "")
            self.auth = self._get_str_from_dict('auth', kwargs, bool, False)
            self.url = self._set_url()
            self._check_proxy_url()
        else:
            ''' 将字符串转化为代理IP字符串(拆分) '''
            self.url = args[0] if len(args) >= 1 else ""
            self.protocol, self.hostname, self.port, self.username, self.password, self.auth = self._parse_str2param()

    @classmethod
    def _get_str_from_dict(cls, o: str, data: dict, _type: any, _default: any):
        """
            从对应的data字典中查找o字段的内容
            如果查询不到内容或是内容类型不是 _type 对应的类型，那么返回对应的_default那日容
        :param o: 需要从字段中获取的字段
        :param data: 查询字典
        :param _type: 期待返回的数据类型
        :param _default: 期待返回的数据的默认值
        :return: 字典中对应的数据
        """
        ''' 期待返回数据类型和默认数值不匹配 '''
        if not isinstance(_default, _type):
            ''' [*] 此处应产生警告日志(数据类型和值不匹配) '''
            _type = str
            _default = ""

        _data = data.get(o, None)
        if _data is None:
            return _default
        if not isinstance(_data, _type):
            return _default
        return _data

    def _set_authorized(self) -> str:
        """
            判断是否需要身份验证，构造身份验证信息
        :return: 身份验证消息
        """
        """ 通过判断是否需要身份验证，构造身份验证信息 """
        if self.auth:
            _authorize = f"{self.username}:{self.password}@"
        elif self.username is not None and self.password is not None and (self.username or self.password):
            self.auth = True
            _authorize = f"{self.username if self.username else ''}:{self.password if self.password else ''}@"
        else:
            _authorize = ""
        return _authorize

    def _set_url(self) -> str:
        """
            构建代理URL
        :return: 代理URL
        """
        _authorized = self._set_authorized()
        return f"{self.protocol}://{_authorized}{self.hostname}:{self.port}"

    @classmethod
    def _get_proxy_mode(cls) -> re.Pattern:
        """
            获取代理URL验证的模板
            通过此模板可以校验代理地址是不是符合要求的，如果不符合要求，则当前代理处于不可用状态
        :return: 代理URL验证的模板
        """
        return re.compile(
            "^(?P<protocol>(http|https|socks4|socks5))://(?P<authorize>(([A-Za-z0-9]*:[A-Za-z0-9]*@)?))(?P<hostname>(["
            "A-Za-z0-9.\-]+))(?P<port>(:[0-9]+))(/[A-Za-z0-9./]*)?",
            re.I)

    def _check_proxy_url(self) -> re.Match:
        """
            校验生成的代理URL是否符合要求，符合要求则将is_usable设置为True，否则设置为False
        :return:
        """
        _mode = self._get_proxy_mode()
        groups = _mode.search(self.url)
        if groups is None or not groups:
            self.is_usable = False
        else:
            self.is_usable = True
        return groups

    def _parse_str2param(self) -> (str, str, str, str, str, bool):
        """
            将传入的代理URL地址解析成相应的参数
        :return: 对应参数
        """
        groups = self._check_proxy_url()
        if groups is None:
            self.is_usable = False
            return "", "", "", "", "", False

        _res = list()
        for param in self.PARAM_NAME:
            _res.append(groups.group(param))

        ''' 正则解析后的参数必须是 protocol, authorized, hostname, port 这样子的四个参数 '''
        if len(_res) != 4:
            self.is_usable = False
            return "", "", "", "", "", False
        protocol, authorized, hostname, port = _res

        port = port.replace(":", "")

        ''' 分析验证内容，分解出username和password '''
        if authorized.endswith("@"):
            authorized = authorized[:-1]
        authorized = authorized.split(":")
        if len(authorized) != 2:
            username, password = "", ""
            _is_auth = False
        else:
            username, password = authorized
            ''' 判断代理是否不需要验证 '''
            if not username and not password:
                # 如果不需要验证,那么就需要重构代理URL
                _is_auth = False
                self.is_usable = True
                self.url = f"{protocol}://{hostname}:{port}"
            else:
                _is_auth = True
                self.is_usable = True
        return protocol, username, password, hostname, port, _is_auth

    def test_proxy_alive(self, url: str, try_times: int = 5) -> (bool, str):
        """
            代理IP存活性检测
            使用GET协议访问输入的测试地址，如果能够成功访问则代理存活，如果出现报错则代理可能存货
        :param try_times: 访问出现错误最大尝试次数
        :param url: 测试代理IP存活性的URL地址
        :return:(代理能否访问， 提示字符串)
        """
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            print(url, self.protocol, self.url)
            headers = {
                "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"""
            }
            _ = requests.get(url=url, proxies={f"{self.protocol}": self.url}, timeout=(5, 10), verify=False, headers=headers)
            return True, "[+]代理能够使用..."
        except requests.exceptions.ConnectTimeout:
            if try_times > 0:
                return self.test_proxy_alive(url, try_times - 1)
            else:
                self.is_usable = False
                return False, f'[!]代理访问{url}超时...'
        except requests.exceptions.ProxyError as e:
            if try_times > 0:
                return self.test_proxy_alive(url, try_times - 1)
            else:
                self.is_usable = False
                print(e.args.__str__())
                return False, f'[!]代理无法访问{url}...'
        except Exception as e:
            self.is_usable = False
            return False, f'[!]代理访问出现异常...'
