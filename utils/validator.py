import re

def check_password_strength(password: str) -> bool:
    """校验密码强度：含大小写字母+数字，长度≥8位"""
    # 正则表达式：至少1个小写、1个大写、1个数字，长度≥8
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    # re.match()：检查password是否符合pattern规则，符合返回匹配对象，否则返回None
    return re.match(pattern, password) is not None

def check_phone(phone: str) -> bool:
    """校验手机号格式11位纯数字"""
    pattern = r"^\d{11}$"
    return re.match(pattern, phone) is not None

def check_positive_number(value: str, is_int: bool = True) -> bool:
    try:
        if is_int:
            num = int(value)
        else:
            num = float(value)
        return num > 0
    except ValueError:
        return False