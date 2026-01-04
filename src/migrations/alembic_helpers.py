from geoalchemy2.alembic_helpers import include_object as geo_include_object


def include_object(object_, name_, type_, reflected, compare_to):
    """
    只允许创建或修改表/列，不允许删除
    """
    # 先调用 geoalchemy 的 include_object 保持对 geometry 的支持
    if not geo_include_object(object_, name_, type_, reflected, compare_to):
        return False

    # 如果是表
    if type_ == "table":
        # 不删除已有表
        if reflected and compare_to is None:
            return False

    # 如果是列
    if type_ == "column":
        # 不删除已有列
        if reflected and compare_to is None:
            return False

    return True
