from core.ProcessProxy import WebProxy
import uuid
from utils.default import HTTP_REQUEST_PROXY_POOL_MAX_SIZE
from utils.default import HTTP_REQUEST_PROXY_POOL_MIN_SIZE


class ProxyNode(object):
    __slots__ = ("id", "is_node", "value", "next")

    def __init__(self, o: WebProxy or None):
        self.id = str(uuid.uuid4())
        self.is_node = True if isinstance(o, WebProxy) else False
        self.value = o
        self.next = None


class ProxyPool(object):
    HTTP_REQUEST_PROXY_POOL_MAX_SIZE = HTTP_REQUEST_PROXY_POOL_MAX_SIZE
    HTTP_REQUEST_PROXY_POOL_MIN_SIZE = HTTP_REQUEST_PROXY_POOL_MIN_SIZE

    __slots__ = ("length", "size", "pool", "cur")

    def __init__(self, size: int = 5):
        if size < self.HTTP_REQUEST_PROXY_POOL_MIN_SIZE:
            self.size = self.HTTP_REQUEST_PROXY_POOL_MIN_SIZE
        elif size > self.HTTP_REQUEST_PROXY_POOL_MAX_SIZE:
            self.size = self.HTTP_REQUEST_PROXY_POOL_MAX_SIZE
        else:
            self.size = size

        self.length = 0
        self.pool = ProxyNode(None)
        self.pool.next = self.pool
        self.cur = self.pool

    def is_empty(self):
        """
            查看当前代理池是否为空
        :return: True|False
        """
        return self.length == 0

    def is_full(self) -> bool:
        """
            查看当前代理池是否为满
        :return:True|False
        """
        return self.length == self.size

    def add_node(self, node: WebProxy or None):
        """
            使用头插法将节点数据插入单项循环链表中
        :param node: 代理节点
        :return:
        """
        head = self.pool

        _new_node = ProxyNode(node)
        if self.is_empty():
            head.next = _new_node
            _new_node.next = head
            self.length = self.length + 1
            return

        if self.is_full():
            self.delete_node()
        else:
            self.length = self.length + 1

        _new_node.next = head.next
        head.next = _new_node
        return

    def delete_node(self) -> WebProxy or None:
        """
            使用尾删法从单向循环链表中删除节点
        :return: 被删除的节点
        """
        head = self.pool

        if self.is_empty():
            return None

        pre = self.pool
        cur = self.pool.next
        while cur.next.id != head.id:
            pre = pre.next
            cur = cur.next

        pre.next = head
        _value = cur.value
        cur.next = None
        del cur
        return _value

    def search_node_index(self, index: int) -> WebProxy or None:
        """
            查看从头节点开始第index位置处的节点
        :return: 查找的节点
        """
        if self.is_empty():
            return None
        _index = 0
        head = self.pool
        node = self.pool
        while _index < index:
            node = node.next
            _index = _index + 1
            if node == head:
                node = node.next
                continue
        return node

    def search_node_status(self) -> WebProxy or None:
        """
            检测代理池中距离上一次存货节点最相近的节点数据
        :return:
        """
        if self.is_empty():
            return None
        head = self.cur
        node = self.cur.next
        while node != head:
            if not node.is_node:
                node = node.next
            elif node.is_node and not node.value.get_is_usable():
                node = node.next
            elif node.is_node and node.value.get_is_usable():
                self.cur = node
                return node
            else:
                node = node.next
        return None

    def test_node_alive(self, index: int, url: str, try_times: int = 5) -> bool:
        """
            检测代理池中某个节点是否存活
        :param index: 代理池中的某个节点的索引
        :param url: 存活性测试的URL地址
        :param try_times: 访问出现错误最大尝试次数
        :return: True|False
        """
        node = self.search_node_index(index)
        if node is None or not node:
            return False
        status, _ = node.value.check_proxy_alive(url, try_times)
        return status

    def test_all_node_alive(self, url: str, try_times: int = 5) -> bool:
        """
            检测代理池中所有节点是否存活
        :param url: 存活性测试的URL地址
        :param try_times: 访问出现错误最大尝试次数
        :return:True|False
        """
        if self.is_empty():
            return False
        head = self.pool
        node = head.next
        while node != head:
            _, _ = node.value.check_proxy_alive(url, try_times)
            node = node.next
        return True
