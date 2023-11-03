from core.ProcessProxy import WebProxy


class ProxyNode(object):
    __slots__ = ("is_node", "node", "status")

    def __init__(self, o: WebProxy or None):
        self.is_node = True if isinstance(o, WebProxy) else False
        self.node = o


class ProxyPool(object):
    from utils.default import HTTP_REQUEST_PROXY_POOL_MAX_SIZE
    HTTP_REQUEST_PROXY_POOL_MAX_SIZE = HTTP_REQUEST_PROXY_POOL_MAX_SIZE
    from utils.default import HTTP_REQUEST_PROXY_POOL_MIN_SIZE
    HTTP_REQUEST_PROXY_POOL_MIN_SIZE = HTTP_REQUEST_PROXY_POOL_MIN_SIZE

    def __init__(self, size: int = 5):
        if size < self.HTTP_REQUEST_PROXY_POOL_MIN_SIZE:
            self.size = self.HTTP_REQUEST_PROXY_POOL_MIN_SIZE
        elif size > self.HTTP_REQUEST_PROXY_POOL_MAX_SIZE:
            self.size = self.HTTP_REQUEST_PROXY_POOL_MAX_SIZE
        else:
            self.size = size
        self.pool = list()
        self.node_cnt = 0
        for _ in range(self.size):
            self.pool.append(ProxyNode(None))

    def test_index_legal(self, index: int) -> bool:
        """
            判断索引是否合理
        :param index: 索引值
        :return: True|False
        """
        return 0 <= index <= self.size

    def test_index_node_legal(self, index: int) -> bool:
        """
            判断索引指向的代理节点是否合理
        :param index: 索引值
        :return: True|False
        """
        _test = self.test_index_legal(index)
        if not _test:
            return False
        return self.pool[index].is_node

    def get_node_cnt(self) -> int:
        """
            获取当前池中有效节点个数
        :return: 有效节点个数
        """
        node_cnt = 0
        for index in range(self.size):
            cur = self.pool[index]
            if cur.is_node:
                node_cnt = node_cnt + 1
        self.node_cnt = node_cnt
        return node_cnt

    def is_empty(self):
        """
            查看当前代理池是否为空
        :return: True|False
        """

        return self.get_node_cnt() == 0

    def is_full(self) -> bool:
        """
            查看当前代理池是否为满
        :return:True|False
        """
        return self.get_node_cnt() == self.size

    def update_node(self, node: WebProxy, index: int) -> bool:
        """
            根据index索引修改pool池子中的节点内容
        :param node: 新节点信息
        :param index: 索引
        :return:True|False
        """
        if index < 0 or index >= self.size:
            return False
        self.pool[index] = ProxyNode(node)
        self.get_node_cnt()
        return True

    def delete_node(self, index: int) -> WebProxy or None:
        """
            删除位于index节点处的pool池中内容
        :param index: 索引节点
        :return:WebProxy or None 被删除的节点内容
        """
        if self.is_empty():
            return None
        if not self.pool[index].is_node:
            return None
        _node = self.pool[index].node
        self.pool[index].node = None
        self.get_node_cnt()
        return _node

    @classmethod
    def test_node_alive(cls, node: WebProxy, url: str, try_times: int = 5) -> bool:
        """
            检测代理池中某个节点是否存活
        :param node: 代理池中的某个节点
        :param url: 存活性测试的URL地址
        :param try_times: 访问出现错误最大尝试次数
        :return: True|False
        """
        status, _ = node.test_proxy_alive(url, try_times)
        return status

    def is_alive(self, index: int, url: str, try_times: int = 5) -> bool:
        """
            检测代理池中某个节点是否存活
        :param index: 代理池中的某个节点的索引
        :param url: 存活性测试的URL地址
        :param try_times: 访问出现错误最大尝试次数
        :return:True|False
        """
        if not self.test_index_node_legal(index):
            return False
        status = self.test_node_alive(self.pool[index].node, url, try_times)
        return status

    def _get_node_attribute(self, index: int, k: str) -> (bool, any):
        """
            查找代理池中指定索引index对象的k属性
        :param index:索引值
        :param k:需要获取的属性键
        :return:True|False, 属性值
        """
        if not self.test_index_node_legal(index):
            return False, None
        if k not in dir(self.pool[index].node):
            return False, None
        return True, self.pool[index].node.__getattribute__(k)

    def node_get_active(self, index: int) -> (bool, any):
        return self._get_node_attribute(index, 'is_active')

    def node_get_usage(self, index: int) -> (bool, any):
        return self._get_node_attribute(index, 'is_usable')

    def _set_node_attribute(self, index: int, k: str, v: any) -> bool:
        """
            为代理池中指定索引index对象的k属性设置值value
        :param index:索引值
        :param k:需要设置的属性键
        :param v:需要设置的属性值
        :return:True|False
        """
        if not self.test_index_node_legal(index):
            return False
        if k not in dir(self.pool[index].node):
            return False
        self.pool[index].node.__setattr__(k, v)
        return True

    def node_set_active(self, index: int, value: bool) -> (bool, any):
        return self._set_node_attribute(index, 'is_active', value)

    def get_proxy_url(self, index: int) -> str:
        """
            通过索引index获取到代理池中对应的代理对象
        :param index: 索引值
        :return: url
        """
        if not self.test_index_node_legal(index):
            return ""
        _usage = self.node_get_usage(index)
        if not _usage:
            return ""
        _status, _res = self._get_node_attribute(index, 'url')
        if not _status:
            return ""
        else:
            return _res

    def _get_proxy_index(self) -> int:
        """
            获取代理池中当前状况下存在的最近的一个代理节点
        :return: 索引值
        """
        if self.is_empty():
            return -1
        index = 0
        while index < self.size:
            cur = self.pool[index]
            if not cur.is_node:
                index = index + 1
            else:
                _usage = cur.node.is_usable
                if not _usage:
                    index = index + 1
                else:
                    return index
        return -1

    def get_proxy(self) -> str:
        """
            获取代理地址对象
        :return: proxy
        """
        index = self._get_proxy_index()
        if not self.test_index_legal(index):
            return ""
        return self.get_proxy_url(index)

    def get_nodes_list(self) -> list:
        """
            获取所有存在的代理对象
        :return: 代理对象集合
        """
        _res = list()
        for index in range(self.size):
            if self.test_index_node_legal(index):
                _res.append(self.pool[index].node)
        return _res

    def get_random_proxy(self) -> str:
        import random
        proxy_lists = self.get_nodes_list()
        cur = random.choice(proxy_lists)
        if not isinstance(cur, WebProxy):
            return ""
        if not cur.is_usable:
            return ""
        return cur.url
