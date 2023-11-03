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
    from utils.default import HTTP_REQUEST_PROXY_PROTOCOL
    # web端请求数据使用代理时允许使用的代理协议类型
    HTTP_REQUEST_PROXY_PROTOCOL = HTTP_REQUEST_PROXY_PROTOCOL
    # 构建代理 URL 所需要的参数名称
    PARAM_NAME = ['protocol', 'authorize', 'hostname', 'port']

    __slots__ = ('_url', '_url_list',
                 '_is_auth', '_is_active', '_is_usable')

    def __init__(self, url: str):
        self._is_active = False
        self._is_usable = True
        self._url = url
        self._url_list, self._is_auth = self._parse_str2param()
        ''' 根据分析结果修正url属性 '''
        self._url = self._set_url()

    ####################################################################################################################
    # 设置类的 get 方法
    ####################################################################################################################
    def get_is_active(self) -> bool:
        return self._is_active

    def get_is_usable(self) -> bool:
        return self._is_usable

    def get_url(self):
        return self._url

    def get_url_list(self):
        return self._url_list

    ####################################################################################################################
    # 设置类的 set 方法
    ####################################################################################################################
    def set_is_active(self, v: bool):
        self._is_active = v

    def switch_active(self):
        self._is_active = not self._is_active

    def set_url(self, url: str):
        self._url = url
        groups = self._check_proxy_url()
        if groups is None or not groups:
            self._url = ""
            self._url_list = {
                'protocol': "",
                'hostname': "",
                'port': "",
                'username': "",
                'password': ""
            }
        else:
            self._url_list = self._parse_str2param()

    def _set_authorized(self) -> str:
        """
            根据是否需要进行身份验证，重新构造身份验证信息
        :return: 身份验证消息
        """
        """ 通过判断是否需要身份验证，构造身份验证信息 """
        if self._is_auth:
            _authorize = f"{self._url_list['username']}:{self._url_list['password']}@"
        elif self._url_list['username'] is not None and self._url_list['password'] is not None \
                and (self._url_list['username'] or self._url_list['password']):
            self._is_auth = True
            _authorize = f"{self._url_list['username'] if self._url_list['username'] else ''}:{self._url_list['password'] if self._url_list['password'] else ''}@"
        else:
            _authorize = ""
        return _authorize

    def _set_url(self) -> str:
        """
            根据重构的URL重构代理URL
        :return: 重构的代理URL
        """
        _authorized = self._set_authorized()
        if self._is_usable:
            return f"{self._url_list['protocol']}://{_authorized}{self._url_list['hostname']}:{self._url_list['port']}"
        else:
            return ""

    ####################################################################################################################
    # 内容校验模板
    ####################################################################################################################
    @classmethod
    def _check_proxy_mode(cls) -> re.Pattern:
        """
            获取代理网络地址校验模板
            通过代理网络地址校验模板可以校验代理地址是不是符合要求的
                如果不符合要求，则当前代理处于不可用状态（self._is_usable = False）
                如果符合要求，则当前代理处于不可用状态（self._is_usable = True）
        :return: 代理网络地址校验模板
        """
        return re.compile(
            "^(?P<protocol>(http|https|socks4|socks5))://(?P<authorize>(([A-Za-z0-9]*:[A-Za-z0-9]*@)?))(?P<hostname>(["
            "A-Za-z0-9.\-]+))(?P<port>(:[0-9]+))(/[A-Za-z0-9./]*)?",
            re.I)

    ####################################################################################################################
    # 内容校验函数
    ####################################################################################################################
    def _check_proxy_url(self) -> re.Match:
        """
            校验self._url的代理网络地址是否符合代理网络地址校验模板眼球
        :return: 模板匹配项参数 包含（protocol,authorize,hostname, port）
        """
        _mode = self._check_proxy_mode()
        groups = _mode.search(self._url)

        if groups is None or not groups:
            self._is_usable = False
        else:
            self._is_usable = True
        return groups

    ####################################################################################################################
    # 解析内容函数
    ####################################################################################################################
    def _parse_str2param(self) -> (dict, bool):
        """
            将传入的代理URL地址解析成相应的参数报文
        :return: 对应参数, True| False
        """
        _url_list = {
            'protocol': "",
            'hostname': "",
            'port': "",
            'username': "",
            'password': ""
        }

        groups = self._check_proxy_url()
        if groups is None:
            self._is_usable = False
            return _url_list, False

        ''' 根据 protocol, authorized, hostname, port 参数定义的顺序进行解包 '''
        _res = list()
        for param in self.PARAM_NAME:
            _res.append(groups.group(param))
        if len(_res) != 4:
            self._is_usable = False
            return _url_list, False
        protocol, authorized, hostname, port = _res

        # 去掉匹配过程中出现的冗余内容
        port = port.replace(":", "")
        authorized = authorized[:-1] if authorized.endswith("@") else authorized
        authorized = authorized.split(":")
        if len(authorized) != 2:
            username, password = "", ""
            _is_auth = False
        else:
            username, password = authorized
            ''' 根据分析出来的参数判断代理是否不需要验证 '''
            if not username and not password:
                _is_auth = False
                self._is_usable = True
                # 如果不需要验证,那么就需要重构代理URL
                self._url = f"{protocol}://{hostname}:{port}"
            else:
                _is_auth = True
                self._is_usable = True

        _url_list['protocol'] = protocol
        _url_list['hostname'] = hostname
        _url_list['port'] = port
        _url_list['username'] = username
        _url_list['password'] = password

        return _url_list, _is_auth

    def check_proxy_alive(self, url: str, try_times: int = 5) -> (bool, str):
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
            _ = requests.get(url=url, proxies=self.show_proxy(),
                             timeout=(5, 10), verify=False)
            self._is_usable = True
            return True, "[+]代理能够使用..."
        except requests.exceptions.ConnectTimeout:
            if try_times > 0:
                return self.check_proxy_alive(url, try_times - 1)
            else:
                self._is_usable = False
                return False, f'[!]代理访问{url}超时...'
        except requests.exceptions.ProxyError as e:
            if try_times > 0:
                return self.check_proxy_alive(url, try_times - 1)
            else:
                self._is_usable = False
                print(e.args.__str__())
                return False, f'[!]代理无法访问{url}...'
        except Exception:
            self._is_usable = False
            return False, f'[!]代理访问出现异常...'

    def show_proxy(self) -> dict:
        return {f"{self._url_list['protocol']}": self._url}
