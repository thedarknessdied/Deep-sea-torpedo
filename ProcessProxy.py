import re


class WebProxy(object):
    """
        WebProxy用来构造一个适用于HTTP/HTTPS请求的服务代理
        ================================================================
        url(required): 完整的代理UTL请求地址
        protocol: 代理URL所使用的协议(HTTP/HTTPS/SOCKS4/SOCKS5)
        username: 代理URL身份验证用户名
        password: 代理URL身份验证密码
        hostname: 代理URL请求地址
        port: 代理URL请求端口
        auth: 代理URL是否需要身份验证
        is_active: 代理URL是否处于开启状态(只有处于活跃状态的代理才能够进行任务)
        is_usable: 代理URL是否合法、合规
    """
    __slots__ = ('url', 'protocol', 'username', 'password', 'hostname', 'port', 'auth',
                 'is_active', 'is_usable')

    from utils.default import HTTP_REQUEST_PROXY_PROTOCOL
    # web端请求数据使用代理时允许使用的代理协议类型
    HTTP_REQUEST_PROXY_PROTOCOL = HTTP_REQUEST_PROXY_PROTOCOL
    # 构建代理 URL 所需要的参数名称
    PARAM_NAME = ['protocol', 'authorize', 'hostname', 'port']

    def __init__(self, url: str):
        self.is_active = False
        self.is_usable = True
        self.url = url
        self.protocol, self.hostname, self.port, self.username, self.password, self.auth = self._parse_str2param()
        ''' 根据分析结果修正url属性 '''
        self.url = self._set_url()

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
        return protocol, hostname, port, username, password, _is_auth

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
            _ = requests.get(url=url, proxies={f"{self.protocol}": self.url}, timeout=(5, 10), verify=False)
            self.is_usable = True
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

    def switch_active(self):
        return not self.is_active
