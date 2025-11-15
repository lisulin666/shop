from typing import List, Tuple, Optional, Dict
import json
import os
from model.entities import User, Product, Order
from utils.log_config import logger
import datetime

# 数据文件绝对路径配置，后续可以修改
DATA_FILE = "mall_data.txt"       # 主数据文件
BACKUP_FILE = "mall_backup.txt"   # 备份文件

def load_data() -> Tuple[List[User], List[Product], List[Order]]:
    """加载数据：从主文件读取，返回用户/商品/订单列表"""
    try:
        if not os.path.exists(DATA_FILE):
            logger.info("", extra={
                "user": "system",
                "operation": "load_data",
                "response_time": "0.0s",
                "result": "success: 数据文件不存在，返回空列表"
            })
            return [], [], []

        # 读取文件（UTF-8编码）
        with open(DATA_FILE, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        # 转换JSON数据为实体类
        users = _json_to_users(data.get("users", []))
        products = _json_to_products(data.get("products", []))
        orders = _json_to_orders(data.get("orders", []))

        logger.info("", extra={
            "user": "system",
            "operation": "load_data",
            "response_time": "0.0s",
            "result": f"success: 加载用户{len(users)}个，商品{len(products)}个，订单{len(orders)}个"
        })
        return users, products, orders

    except Exception as e:
        logger.error("", extra={
            "user": "system",
            "operation": "load_data",
            "response_time": "0.0s",
            "result": f"fail: {str(e)}"
        })
        return [], [], []

def save_data(users: List[User], products: List[Product], orders: List[Order]) -> bool:
    """保存数据：将实体类列表写入主文件（供Service层调用）"""
    try:
        # 转换实体类为JSON可序列化的字典
        data = {
            "users": [user.to_dict() for user in users],
            "products": [prod.to_dict() for prod in products],
            "orders": [order.to_dict() for order in orders]
        }

        # 写入文件（UTF-8编码，格式化输出）
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("", extra={
            "user": "system",
            "operation": "save_data",
            "response_time": "0.0s",
            "result": f"success: 保存用户{len(users)}个，商品{len(products)}个，订单{len(orders)}个"
        })
        return True

    except Exception as e:
        logger.error("", extra={
            "user": "system",
            "operation": "save_data",
            "response_time": "0.0s",
            "result": f"fail: {str(e)}"
        })
        return False

def backup_data() -> bool:
    """备份数据：将主文件复制到备份文件（供Service层调用）"""
    try:
        if not os.path.exists(DATA_FILE):
            logger.warning("", extra={
                "user": "system",
                "operation": "backup_data",
                "response_time": "0.0s",
                "result": "warn: 主数据文件不存在，无法备份"
            })
            return False

        # 读取主文件并写入备份文件
        with open(DATA_FILE, "r", encoding="utf-8") as f_in, \
             open(BACKUP_FILE, "w", encoding="utf-8") as f_out:
            json.dump(json.load(f_in), f_out, ensure_ascii=False, indent=2)

        logger.info("", extra={
            "user": "system",
            "operation": "backup_data",
            "response_time": "0.0s",
            "result": "success: 数据备份完成"
        })
        return True

    except Exception as e:
        logger.error("", extra={
            "user": "system",
            "operation": "backup_data",
            "response_time": "0.0s",
            "result": f"fail: {str(e)}"
        })
        return False

def restore_data() -> Tuple[List[User], List[Product], List[Order], bool]:
    """恢复数据：从备份文件加载数据（供Service层调用）"""
    try:
        if not os.path.exists(BACKUP_FILE):
            logger.warning("", extra={
                "user": "system",
                "operation": "restore_data",
                "response_time": "0.0s",
                "result": "warn: 备份文件不存在，无法恢复"
            })
            return [], [], [], False

        # 读取备份文件
        with open(BACKUP_FILE, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        # 转换为实体类
        users = _json_to_users(data.get("users", []))
        products = _json_to_products(data.get("products", []))
        orders = _json_to_orders(data.get("orders", []))

        logger.info("", extra={
            "user": "system",
            "operation": "restore_data",
            "response_time": "0.0s",
            "result": f"success: 从备份恢复用户{len(users)}个，商品{len(products)}个，订单{len(orders)}个"
        })
        return users, products, orders, True

    except Exception as e:
        logger.error("", extra={
            "user": "system",
            "operation": "restore_data",
            "response_time": "0.0s",
            "result": f"fail: {str(e)}"
        })
        return [], [], [], False

# ------------------------------ 内部辅助函数（不对外暴露） ------------------------------
def _json_to_users(json_list: List[Dict]) -> List[User]:
    """JSON列表转为User实体列表"""
    users = []
    for item in json_list:
        user = User(
            username=item.get("username", ""),
            password=item.get("password", ""),
            is_super=item.get("is_super", False)
        )
        user.login_fail_count = item.get("login_fail_count", 0)
        user.lock_time = item.get("lock_time", 0)
        users.append(user)
    return users

def _json_to_products(json_list: List[Dict]) -> List[Product]:
    """JSON列表转为Product实体列表"""
    products = []
    for item in json_list:
        try:
            product = Product(
                product_id=item.get("product_id", ""),
                name=item.get("name", ""),
                category=item.get("category", ""),
                price=float(item.get("price", 0)),
                stock=int(item.get("stock", 0))
            )
            products.append(product)
        except (ValueError, TypeError):
            logger.warning("", extra={
                "user": "system",
                "operation": "_json_to_products",
                "response_time": "0.0s",
                "result": f"warn: 无效商品数据{item}，跳过"
            })
    return products

def _json_to_orders(json_list: List[Dict]) -> List[Order]:
    """JSON列表转为Order实体列表"""
    orders = []
    for item in json_list:
        try:
            # 解析下单时间（字符串转datetime）
            create_time = datetime.datetime.strptime(
                item.get("create_time", ""), "%Y-%m-%d %H:%M:%S"
            )
            order = Order(
                order_id=item.get("order_id", ""),
                phone=item.get("phone", ""),
                product_id=item.get("product_id", ""),
                buy_count=int(item.get("buy_count", 0)),
                product_price=float(item.get("product_price", 0))
            )
            order.create_time = create_time  # 覆盖默认时间
            orders.append(order)
        except (ValueError, TypeError):
            logger.warning("", extra={
                "user": "system",
                "operation": "_json_to_orders",
                "response_time": "0.0s",
                "result": f"warn: 无效订单数据{item}，跳过"
            })
    return orders