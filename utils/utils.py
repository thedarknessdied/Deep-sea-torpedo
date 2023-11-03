def get_str_from_dict(o: str, data: dict, _type: any, _default: any):
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

