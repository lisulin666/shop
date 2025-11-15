from typing import List, Optional, Dict
from model.entities import Product, Order
from service.mall_service import MallSystem
from typing import List, Tuple, Optional, Dict  # 确保包含 Tuple

def get_login_input() -> Tuple[str, str]:
    """获取登录输入：返回（用户名，密码）"""
    print("\n===== 管理员登录 =====")
    username = input("请输入用户名：").strip()
    password = input("请输入密码：").strip()
    return username, password

def show_main_menu() -> str:
    """显示主菜单：返回用户选择"""
    print("\n" + "="*40)
    print("        在线商城订单管理系统")
    print("="*40)
    print("1. 添加商品信息        2. 查看所有商品")
    print("3. 删除商品信息        4. 修改商品信息")
    print("5. 创建用户订单        6. 查询订单信息")
    print("7. 撤销订单            8. 订单统计分析")
    print("9. 手动备份数据        10. 恢复数据")
    print("11. 查询系统日志       12. 清理系统日志")
    print("13. 退出系统")
    print("="*40)
    return input("请选择功能（1-13）：").strip()

def get_product_input() -> Tuple[str, str, str, str, str]:
    """获取添加商品输入：返回（编号，名称，分类，单价，库存）"""
    print("\n===== 添加商品 =====")
    product_id = input("请输入商品编号：").strip()
    name = input("请输入商品名称：").strip()
    category = input("请输入商品分类：").strip()
    price = input("请输入商品单价（>0）：").strip()
    stock = input("请输入库存数量（>0）：").strip()
    return product_id, name, category, price, stock

def show_products(products: List[Product]) -> None:
    """显示所有商品：表格格式"""
    print("\n===== 所有商品信息 =====")
    if not products:
        print("系统中暂无商品信息！")
        return
    # 表头
    print(f"{'商品编号':<12} {'商品名称':<15} {'分类':<10} {'单价（元）':<12} {'库存':<8} {'总价值（元）':<12}")
    print("-" * 70)
    # 商品数据
    for prod in products:
        print(f"{prod.product_id:<12} {prod.name:<15} {prod.category:<10} "
              f"{prod.price:<12.2f} {prod.stock:<8} {prod.total_value:<12.2f}")

def get_delete_product_input() -> str:
    """获取删除商品输入：返回商品编号"""
    print("\n===== 删除商品 =====")
    return input("请输入要删除的商品编号：").strip()

def get_modify_product_input() -> Tuple[str, str, str]:
    """获取修改商品输入：返回（商品编号，修改字段，新值）"""
    print("\n===== 修改商品 =====")
    product_id = input("请输入要修改的商品编号：").strip()
    # 显示修改字段选项
    print("\n可修改字段：")
    print("1. 商品名称    2. 商品分类    3. 单价    4. 库存")
    field_choice = input("请选择修改字段（1-4）：").strip()
    # 映射字段（1→name，2→category，3→price，4→stock）
    field_map = {"1": "name", "2": "category", "3": "price", "4": "stock"}
    field = field_map.get(field_choice, "")
    if not field:
        return product_id, "", ""
    # 获取新值
    field_name = {"name": "商品名称", "category": "商品分类", "price": "单价", "stock": "库存"}[field]
    new_value = input(f"请输入新的{field_name}：").strip()
    return product_id, field, new_value

def get_order_input() -> Tuple[str, str, str, str]:
    """获取创建订单输入：返回（订单编号，手机号，商品编号，购买数量）"""
    print("\n===== 创建订单 =====")
    order_id = input("请输入订单编号：").strip()
    phone = input("请输入用户手机号（11位数字）：").strip()
    product_id = input("请输入商品编号：").strip()
    buy_count = input("请输入购买数量：").strip()
    return order_id, phone, product_id, buy_count

def show_order(order: Optional[Order], products: List[Product]) -> None:
    """显示订单详情：关联商品信息"""
    print("\n===== 订单详细信息 =====")
    if not order:
        print("订单不存在！")
        return
    # 查找关联商品
    product = next((p for p in products if p.product_id == order.product_id), None)
    product_name = product.name if product else "未知商品"
    # 显示详情
    print(f"订单编号：{order.order_id}")
    print(f"用户手机号：{order.phone}")
    print(f"商品信息：{product_name}（编号：{order.product_id}）")
    print(f"购买数量：{order.buy_count}")
    print(f"下单单价：{order.product_price:.2f} 元")
    print(f"订单总金额：{order.total_amount:.2f} 元")
    print(f"下单时间：{order.create_time.strftime('%Y-%m-%d %H:%M:%S')}")

def get_order_id_input(prompt: str) -> str:
    """获取订单编号输入：prompt为提示文本"""
    print(f"\n===== {prompt} =====")
    return input("请输入订单编号：").strip()

def show_statistics(stats: Dict[str, Dict[str, float]]) -> None:
    """显示订单统计结果"""
    print("\n===== 订单统计分析 =====")
    if not stats:
        print("暂无订单数据，无法统计！")
        return
    # 表头
    print(f"{'商品分类':<12} {'销售数量':<12} {'销售总额（元）':<15}")
    print("-" * 40)
    # 统计数据
    total_count = 0
    total_amount = 0.0
    for category, data in stats.items():
        count = int(data["sales_count"])
        amount = round(data["sales_amount"], 2)
        print(f"{category:<12} {count:<12} {amount:<15.2f}")
        total_count += count
        total_amount += amount
    # 总计
    print("-" * 40)
    print(f"{'总计':<12} {total_count:<12} {total_amount:<15.2f}")

def show_logs(logs: List[str]) -> None:
    """显示日志列表"""
    print("\n===== 系统日志（最近10条） =====")
    if not logs:
        print("暂无日志记录！")
        return
    for i, log in enumerate(logs, 1):
        print(f"{i:2d}. {log}")

def confirm_operation(prompt: str) -> bool:
    """确认操作：prompt为确认提示，返回是否确认（y/Y为是）"""
    confirm = input(f"{prompt}（y/Y确认，其他取消）：").strip().lower()
    return confirm == "y"