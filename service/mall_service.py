from typing import List, Optional, Dict
import time
from model.entities import User, Product, Order
from dao.data_handler import load_data, save_data, backup_data, restore_data
from utils.validator import check_password_strength, check_phone, check_positive_number
from utils.log_config import logger
import os
from typing import List, Tuple, Optional, Dict

class MallSystem:
    """商城系统业务核心：处理权限、商品、订单等业务逻辑"""
    def __init__(self):
        # 初始化数据（从DAO层加载）
        self.users: List[User] = []
        self.products: List[Product] = []
        self.orders: List[Order] = []
        self.current_user: Optional[User] = None  # 当前登录用户
        self._load_initial_data()  # 加载数据
        self._init_default_users()  # 初始化默认管理员（无数据时）

    def _load_initial_data(self) -> None:
        """加载初始数据：调用DAO层接口"""
        self.users, self.products, self.orders = load_data()

    def _init_default_users(self) -> None:
        """初始化默认管理员（无用户数据时）"""
        if not self.users:
            # 超级管理员（admin/Admin1234）、普通管理员（user1/User123456）
            super_user = User("lsl", "Lsl123", is_super=True)
            normal_user = User("user1", "User123456", is_super=False)
            self.users.extend([super_user, normal_user])
            save_data(self.users, self.products, self.orders)  # 保存到DAO
            logger.info("", extra={
                "user": "system",
                "operation": "_init_default_users",
                "response_time": "0.0s",
                "result": "success: 初始化默认管理员账号"
            })

    def _log_operation(self, operation: str, result: str, start_time: float) -> None:
        """记录操作日志（内部调用）"""
        response_time = round(time.time() - start_time, 4)
        logger.info("", extra={
            "user": self.current_user.username if self.current_user else "anonymous",
            "operation": operation,
            "response_time": f"{response_time}s",
            "result": result
        })

    # ------------------------------ 权限管理业务 ------------------------------
    def login(self, username: str, password: str) -> bool:
        """管理员登录：返回是否成功"""
        start_time = time.time()
        user = next((u for u in self.users if u.username == username), None)
        if not user:
            self._log_operation("login", "fail: 用户名不存在", start_time)
            return False

        # 检查账号锁定（3次失败锁定30秒）
        current_time = time.time()
        if user.login_fail_count >= 3 and current_time - user.lock_time < 30:
            remaining = 30 - (current_time - user.lock_time)
            self._log_operation("login", f"fail: 账号锁定，剩余{remaining:.0f}秒", start_time)
            return False

        if user.password == password:
            user.login_fail_count = 0  # 重置失败次数
            self.current_user = user
            self._log_operation("login", f"success: {username}登录", start_time)
            return True
        else:
            user.login_fail_count += 1
            user.lock_time = current_time
            remaining = 3 - user.login_fail_count
            self._log_operation("login", f"fail: 密码错误，剩余{remaining}次", start_time)
            return False

    def check_permission(self, require_super: bool = False) -> bool:
        """权限检查：require_super=True需超级管理员"""
        if not self.current_user:
            logger.warning("", extra={
                "user": "anonymous",
                "operation": "check_permission",
                "response_time": "0.0s",
                "result": "fail: 未登录"
            })
            return False
        if require_super and not self.current_user.is_super:
            logger.warning("", extra={
                "user": self.current_user.username,
                "operation": "check_permission",
                "response_time": "0.0s",
                "result": "fail: 普通管理员无权限"
            })
            return False
        return True

    def modify_user(self, old_username: str, new_username: str, new_password: str) -> Tuple[bool, str]:
        """修改用户信息（示例方法）"""
        start_time = time.time()

        # 1. 权限检查（只有超级管理员能修改）
        if not self.check_permission(require_super=True):
            self._log_operation("modify_user", "fail: 无权限", start_time)
            return False, "无权限修改用户信息"

        # 2. 查找用户
        user = next((u for u in self.users if u.username == old_username), None)
        if not user:
            self._log_operation("modify_user", f"fail: 用户{old_username}不存在", start_time)
            return False, "用户不存在"

        # 3. 检查新用户名是否已被占用（如果修改用户名）
        if new_username != old_username and any(u.username == new_username for u in self.users):
            self._log_operation("modify_user", f"fail: 新用户名{new_username}已存在", start_time)
            return False, "新用户名已被占用"

        # 4. 验证新密码强度（调用工具层的校验函数）
        if not check_password_strength(new_password):
            self._log_operation("modify_user", "fail: 密码强度不足", start_time)
            return False, "密码需包含大小写字母+数字，长度≥8位"

        # 5. 更新用户信息（关键：修改内存中的self.users列表）
        user.username = new_username  # 修改用户名
        user.password = new_password  # 修改密码

        # 6. 保存到文件（关键：持久化修改，否则重启后丢失）
        save_success = save_data(self.users, self.products, self.orders)
        if not save_success:
            self._log_operation("modify_user", "fail: 数据保存失败", start_time)
            return False, "修改失败，数据保存出错"

        # 7. 记录日志
        self._log_operation("modify_user", f"success: {old_username}修改为{new_username}", start_time)
        return True, "修改成功"
    # ------------------------------ 商品管理业务 ------------------------------
    def add_product(self, product_id: str, name: str, category: str, price: str, stock: str) -> Tuple[bool, str]:
        """添加商品：返回（是否成功，提示信息）"""
        start_time = time.time()
        # 权限检查（普通管理员可操作）
        if not self.check_permission(require_super=False):
            self._log_operation("add_product", "fail: 权限不足", start_time)
            return False, "权限不足：请先登录"

        # 验证商品编号唯一
        if any(p.product_id == product_id for p in self.products):
            self._log_operation("add_product", f"fail: 商品编号{product_id}重复", start_time)
            return False, "商品编号已存在，请重新输入"

        # 验证单价（正浮点数）
        if not check_positive_number(price, is_int=False):
            self._log_operation("add_product", f"fail: 单价{price}无效", start_time)
            return False, "单价必须是大于0的数字"

        # 验证库存（正整数）
        if not check_positive_number(stock, is_int=True):
            self._log_operation("add_product", f"fail: 库存{stock}无效", start_time)
            return False, "库存必须是大于0的整数"

        # 创建商品并保存
        product = Product(product_id, name, category, float(price), int(stock))
        self.products.append(product)
        save_success = save_data(self.users, self.products, self.orders)
        if save_success:
            self._log_operation("add_product", f"success: {product_id}", start_time)
            return True, "添加成功"
        else:
            self.products.remove(product)  # 回滚
            self._log_operation("add_product", "fail: 数据保存失败", start_time)
            return False, "添加失败：数据保存异常"

    def get_all_products(self) -> List[Product]:
        """获取所有商品：供View层显示"""
        start_time = time.time()
        if not self.check_permission(require_super=False):
            self._log_operation("get_all_products", "fail: 权限不足", start_time)
            return []
        self._log_operation("get_all_products", f"success: {len(self.products)}个商品", start_time)
        return self.products

    def delete_product(self, product_id: str) -> Tuple[bool, str]:
        """删除商品：返回（是否成功，提示信息）- 需超级管理员"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("delete_product", "fail: 权限不足", start_time)
            return False, "权限不足：仅超级管理员可删除"

        # 查找商品
        product = next((p for p in self.products if p.product_id == product_id), None)
        if not product:
            self._log_operation("delete_product", f"fail: {product_id}不存在", start_time)
            return False, "删除失败：商品不存在"

        # 删除并保存
        self.products.remove(product)
        save_success = save_data(self.users, self.products, self.orders)
        if save_success:
            self._log_operation("delete_product", f"success: {product_id}", start_time)
            return True, "删除成功"
        else:
            self.products.append(product)  # 回滚
            self._log_operation("delete_product", "fail: 数据保存失败", start_time)
            return False, "删除失败：数据保存异常"

    def modify_product(self, product_id: str, field: str, new_value: str) -> Tuple[bool, str]:
        """修改商品：field=name/category/price/stock，返回（是否成功，提示信息）"""
        start_time = time.time()
        if not self.check_permission(require_super=False):
            self._log_operation("modify_product", "fail: 权限不足", start_time)
            return False, "权限不足：请先登录"

        # 查找商品
        product = next((p for p in self.products if p.product_id == product_id), None)
        if not product:
            self._log_operation("modify_product", f"fail: {product_id}不存在", start_time)
            return False, "修改失败：商品不存在"

        # 验证新值并修改
        try:
            if field == "name":
                product.name = new_value
            elif field == "category":
                product.category = new_value
            elif field == "price":
                if not check_positive_number(new_value, is_int=False):
                    self._log_operation("modify_product", f"fail: 单价{new_value}无效", start_time)
                    return False, "单价必须是大于0的数字"
                product.price = float(new_value)
            elif field == "stock":
                if not check_positive_number(new_value, is_int=True):
                    self._log_operation("modify_product", f"fail: 库存{new_value}无效", start_time)
                    return False, "库存必须是大于0的整数"
                product.stock = int(new_value)
            else:
                self._log_operation("modify_product", f"fail: 字段{field}不存在", start_time)
                return False, "无效字段：仅支持名称/分类/单价/库存"

            # 保存修改
            save_success = save_data(self.users, self.products, self.orders)
            if save_success:
                self._log_operation("modify_product", f"success: {product_id}-{field}", start_time)
                return True, f"{field}修改成功"
            else:
                self._log_operation("modify_product", "fail: 数据保存失败", start_time)
                return False, "修改失败：数据保存异常"

        except Exception as e:
            self._log_operation("modify_product", f"fail: {str(e)}", start_time)
            return False, f"修改失败：{str(e)}"

    # ------------------------------ 订单管理业务 ------------------------------
    def create_order(self, order_id: str, phone: str, product_id: str, buy_count: str) -> Tuple[bool, str]:
        """创建订单：返回（是否成功，提示信息）- 需超级管理员"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("create_order", "fail: 权限不足", start_time)
            return False, "权限不足：仅超级管理员可创建订单"

        # 验证订单编号唯一
        if any(o.order_id == order_id for o in self.orders):
            self._log_operation("create_order", f"fail: 订单编号{order_id}重复", start_time)
            return False, "订单编号已存在，请重新输入"

        # 验证手机号
        if not check_phone(phone):
            self._log_operation("create_order", f"fail: 手机号{phone}无效", start_time)
            return False, "手机号格式错误：需11位纯数字"

        # 验证商品存在
        product = next((p for p in self.products if p.product_id == product_id), None)
        if not product:
            self._log_operation("create_order", f"fail: 商品{product_id}不存在", start_time)
            return False, "创建失败：商品不存在"

        # 验证购买数量
        if not check_positive_number(buy_count, is_int=True):
            self._log_operation("create_order", f"fail: 数量{buy_count}无效", start_time)
            return False, "购买数量必须是大于0的整数"
        buy_count_int = int(buy_count)
        if buy_count_int > product.stock:
            self._log_operation("create_order", f"fail: 库存不足（需{buy_count_int}，剩{product.stock}）", start_time)
            return False, f"库存不足：当前库存{product.stock}，无法购买{buy_count_int}个"

        # 原子操作：扣库存+创建订单（失败回滚）
        original_stock = product.stock
        try:
            product.stock -= buy_count_int  # 扣库存
            order = Order(order_id, phone, product_id, buy_count_int, product.price)
            self.orders.append(order)  # 加订单
            save_success = save_data(self.users, self.products, self.orders)
            if save_success:
                self._log_operation("create_order", f"success: {order_id}", start_time)
                return True, "订单创建成功"
            else:
                # 回滚
                product.stock = original_stock
                if order in self.orders:
                    self.orders.remove(order)
                self._log_operation("create_order", "fail: 数据保存失败", start_time)
                return False, "创建失败：数据保存异常"
        except Exception as e:
            # 回滚
            product.stock = original_stock
            self._log_operation("create_order", f"fail: {str(e)}", start_time)
            return False, f"创建失败：{str(e)}"

    def get_order(self, order_id: str) -> Optional[Order]:
        """查询订单：返回订单实体（None表示不存在）- 需超级管理员"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("get_order", "fail: 权限不足", start_time)
            return None
        order = next((o for o in self.orders if o.order_id == order_id), None)
        if order:
            self._log_operation("get_order", f"success: {order_id}", start_time)
        else:
            self._log_operation("get_order", f"fail: {order_id}不存在", start_time)
        return order

    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """撤销订单：恢复库存，返回（是否成功，提示信息）- 需超级管理员"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("cancel_order", "fail: 权限不足", start_time)
            return False, "权限不足：仅超级管理员可撤销订单"

        # 查找订单
        order = next((o for o in self.orders if o.order_id == order_id), None)
        if not order:
            self._log_operation("cancel_order", f"fail: {order_id}不存在", start_time)
            return False, "撤销失败：订单不存在"

        # 查找关联商品
        product = next((p for p in self.products if p.product_id == order.product_id), None)
        if not product:
            self._log_operation("cancel_order", f"fail: 商品{order.product_id}不存在", start_time)
            return False, "撤销失败：关联商品不存在"

        # 执行撤销（恢复库存+删除订单）
        try:
            product.stock += order.buy_count  # 恢复库存
            self.orders.remove(order)  # 删除订单
            save_success = save_data(self.users, self.products, self.orders)
            if save_success:
                self._log_operation("cancel_order", f"success: {order_id}", start_time)
                return True, "订单撤销成功，库存已恢复"
            else:
                # 回滚
                product.stock -= order.buy_count
                self.orders.append(order)
                self._log_operation("cancel_order", "fail: 数据保存失败", start_time)
                return False, "撤销失败：数据保存异常"
        except Exception as e:
            self._log_operation("cancel_order", f"fail: {str(e)}", start_time)
            return False, f"撤销失败：{str(e)}"

    # ------------------------------ 统计与备份业务 ------------------------------
    def get_order_statistics(self) -> Dict[str, Dict[str, float]]:
        """订单统计：按分类返回{分类: {销售数量: x, 销售总额: y}}"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("get_order_statistics", "fail: 权限不足", start_time)
            return {}

        stats: Dict[str, Dict[str, float]] = {}
        for order in self.orders:
            product = next((p for p in self.products if p.product_id == order.product_id), None)
            if not product:
                continue
            category = product.category
            if category not in stats:
                stats[category] = {"sales_count": 0, "sales_amount": 0.0}
            stats[category]["sales_count"] += order.buy_count
            stats[category]["sales_amount"] += order.total_amount

        self._log_operation("get_order_statistics", f"success: {len(stats)}个分类", start_time)
        return stats

    def backup_system_data(self) -> Tuple[bool, str]:
        """手动备份数据：返回（是否成功，提示信息）"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("backup_system_data", "fail: 权限不足", start_time)
            return False, "权限不足：仅超级管理员可备份"

        backup_success = backup_data()
        if backup_success:
            self._log_operation("backup_system_data", "success", start_time)
            return True, "手动备份成功"
        else:
            self._log_operation("backup_system_data", "fail", start_time)
            return False, "手动备份失败"

    def restore_system_data(self) -> Tuple[bool, str]:
        """恢复数据：返回（是否成功，提示信息）"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("restore_system_data", "fail: 权限不足", start_time)
            return False, "权限不足：仅超级管理员可恢复"

        users, products, orders, restore_success = restore_data()
        if restore_success:
            self.users = users
            self.products = products
            self.orders = orders
            save_data(self.users, self.products, self.orders)  # 保存到主文件
            self._log_operation("restore_system_data", "success", start_time)
            return True, "数据恢复成功"
        else:
            self._log_operation("restore_system_data", "fail", start_time)
            return False, "数据恢复失败：备份文件不存在或异常"

    def get_recent_logs(self, keyword: Optional[str] = None) -> List[str]:
        """获取最近10条日志：支持关键词过滤"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("get_recent_logs", "fail: 权限不足", start_time)
            return ["权限不足：仅超级管理员可查看日志"]

        logs = []
        log_file = "mall_system.log"
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                logs = f.readlines()
            # 关键词过滤
            if keyword and keyword.strip():
                logs = [log.strip() for log in logs if keyword.lower() in log.lower()]
            else:
                logs = [log.strip() for log in logs]

        # 取最近10条
        recent_logs = logs[-10:] if len(logs) >= 10 else logs
        self._log_operation("get_recent_logs", f"success: {len(recent_logs)}条", start_time)
        return recent_logs

    def clear_logs(self) -> Tuple[bool, str]:
        """清理日志：返回（是否成功，提示信息）"""
        start_time = time.time()
        if not self.check_permission(require_super=True):
            self._log_operation("clear_logs", "fail: 权限不足", start_time)
            return False, "权限不足：仅超级管理员可清理日志"

        log_file = "mall_system.log"
        try:
            if os.path.exists(log_file):
                with open(log_file, "w", encoding="utf-8") as f:
                    f.truncate()  # 清空文件
                self._log_operation("clear_logs", "success", start_time)
                return True, "日志清理成功"
            else:
                self._log_operation("clear_logs", "fail: 日志文件不存在", start_time)
                return False, "清理失败：日志文件不存在"
        except Exception as e:
            self._log_operation("clear_logs", f"fail: {str(e)}", start_time)
            return False, f"清理失败：{str(e)}"

    def exit_system(self) -> None:
        """退出系统：保存数据+自动备份"""
        start_time = time.time()
        # 保存当前数据
        save_data(self.users, self.products, self.orders)
        # 自动备份
        backup_data()
        self._log_operation("exit_system", "success: 数据保存+自动备份", start_time)