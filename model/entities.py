from typing import Dict
import datetime

class User:
    """用户实体：封装管理员信息"""
    def __init__(self, username: str, password: str, is_super: bool = False):
        self.username = username
        self.password = password
        self.is_super = is_super
        self.login_fail_count = 0
        self.lock_time = 0

    def to_dict(self) -> Dict:
        """转为字典：用于JSON序列化（供DAO层存储）"""
        return {
            "username": self.username,
            "password": self.password,
            "is_super": self.is_super,
            "login_fail_count": self.login_fail_count,
            "lock_time": self.lock_time
        }

class Product:
    """商品实体：封装商品信息"""
    def __init__(self, product_id: str, name: str, category: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    def to_dict(self) -> Dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock         #库存
        }

    @property
    def total_value(self) -> float:
        """计算商品总价值（单价×库存）：只读属性，通过property实现"""
        return round(self.price * self.stock, 2)

class Order:
    """订单实体：封装订单信息"""
    def __init__(self, order_id: str, phone: str, product_id: str, buy_count: int, product_price: float):
        self.order_id = order_id
        self.phone = phone
        self.product_id = product_id
        self.buy_count = buy_count
        self.product_price = product_price      #历史订单的金额应该按下单时的价格算，所以必须单独存下单时的价格
        self.total_amount = round(product_price * buy_count, 2)
        self.create_time = datetime.datetime.now()

    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "phone": self.phone,
            "product_id": self.product_id,
            "buy_count": self.buy_count,
            "product_price": self.product_price,
            "total_amount": self.total_amount,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")       #因为时间对象不能直接存到 JSON，必须转成字符串
        }