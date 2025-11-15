from service.mall_service import MallSystem

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.scrolledtext as st

# 初始化业务系统
mall_system = MallSystem()

class MallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("在线商城订单管理系统")
        self.root.geometry("1000x700")  # 窗口大小
        self.current_user = None  # 当前登录用户

        # 初始化登录页（默认显示）
        self.show_login_page()

    # ------------------------------ 登录页 ------------------------------
    def show_login_page(self):
        # 清空窗口所有组件
        for widget in self.root.winfo_children():
            widget.destroy()

        # 登录框布局
        login_frame = ttk.Frame(self.root, padding="50")
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 标题
        ttk.Label(login_frame, text="管理员登录", font=("宋体", 20)).grid(row=0, column=0, columnspan=2, pady=20)

        # 用户名输入
        ttk.Label(login_frame, text="用户名：", font=("宋体", 12)).grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        self.username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.username_var, font=("宋体", 12), width=30).grid(row=1, column=1, padx=10, pady=10)

        # 密码输入
        ttk.Label(login_frame, text="密码：", font=("宋体", 12)).grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        self.password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", font=("宋体", 12), width=30).grid(row=2, column=1, padx=10, pady=10)

        # 登录按钮
        ttk.Button(login_frame, text="登录", command=self.login, width=15).grid(row=3, column=0, columnspan=2, pady=20)

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("警告", "用户名和密码不能为空！")
            return

        # 调用原有登录逻辑
        login_success = mall_system.login(username, password)
        if login_success:
            self.current_user = username
            messagebox.showinfo("成功", f"欢迎{username}登录系统！")
            self.show_main_page()  # 登录成功后显示主功能页
        else:
            messagebox.showerror("失败", "用户名或密码错误！")

    def show_modify_user(self):
            # 清空右侧内容区域
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # 标题（提示只有超级管理员可操作）
            ttk.Label(
                self.content_frame,
                text="修改用户信息（仅超级管理员可用）",
                font=("宋体", 16)
            ).pack(pady=10)

            # 表单框架
            form_frame = ttk.Frame(self.content_frame)
            form_frame.pack(pady=20)

            # 表单字段：原用户名、新用户名、新密码
            fields = [
                ("原用户名：", "old_username"),
                ("新用户名：", "new_username"),
                ("新密码：", "new_password")  # 密码强度要求：大小写+数字，≥8位
            ]
            self.modify_user_vars = {}  # 存储输入框变量

            # 循环创建表单
            for i, (label_text, var_name) in enumerate(fields):
                ttk.Label(form_frame, text=label_text, font=("宋体", 12)).grid(
                    row=i, column=0, sticky=tk.E, padx=10, pady=10
                )
                var = tk.StringVar()
                self.modify_user_vars[var_name] = var
                # 密码框用show="*"隐藏输入
                show = "*" if var_name == "new_password" else ""
                ttk.Entry(
                    form_frame,
                    textvariable=var,
                    font=("宋体", 12),
                    width=30,
                    show=show
                ).grid(row=i, column=1, padx=10, pady=10)

            # 提交按钮
            ttk.Button(
                self.content_frame,
                text="提交修改",
                command=self.modify_user_submit
            ).pack(pady=10)

    def modify_user_submit(self):
        # 获取表单数据（去除前后空格）
        old_username = self.modify_user_vars["old_username"].get().strip()
        new_username = self.modify_user_vars["new_username"].get().strip()
        new_password = self.modify_user_vars["new_password"].get().strip()

        # 简单校验（非空）
        if not old_username or not new_username or not new_password:
            messagebox.showwarning("警告", "所有字段不能为空！")
            return

        # 调用业务层的modify_user方法
        success, msg = mall_system.modify_user(old_username, new_username, new_password)

        # 显示结果
        if success:
            messagebox.showinfo("成功", msg)
            # 清空表单
            for var in self.modify_user_vars.values():
                var.set("")
        else:
            messagebox.showerror("失败", msg)

    # ------------------------------ 主功能页 ------------------------------
    def show_main_page(self):
        # 清空窗口所有组件
        for widget in self.root.winfo_children():
            widget.destroy()

        # 左侧功能菜单
        menu_frame = ttk.Frame(self.root, width=200, style="Menu.TFrame")
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 功能按钮（按原有菜单顺序）
        functions = [
            ("1. 添加商品", self.show_add_product),
            ("2. 查看商品", self.show_view_products),
            ("3. 删除商品", self.show_delete_product),
            ("4. 修改商品", self.show_modify_product),
            ("5. 创建订单", self.show_create_order),
            ("6. 查询订单", self.show_query_order),
            ("7. 撤销订单", self.show_cancel_order),
            ("8. 订单统计", self.show_statistics),
            ("9. 手动备份", self.backup_data),
            ("10. 恢复数据", self.restore_data),
            ("11. 查看日志", self.show_logs),
            ("12. 清理日志", self.clear_logs),
            ("13. 修改用户信息", self.show_modify_user),  # 新增这一行
            ("14. 退出系统", self.exit_system)
        ]

        for text, cmd in functions:
            ttk.Button(menu_frame, text=text, command=cmd, width=18).pack(pady=5)

        # 右侧内容区域（默认显示欢迎信息）
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self.content_frame, text=f"欢迎使用在线商城订单管理系统\n当前用户：{self.current_user}", font=("宋体", 16)).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # ------------------------------ 商品管理功能界面 ------------------------------
    def show_add_product(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="添加商品信息", font=("宋体", 16)).pack(pady=10)

        # 表单框架
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(pady=20)

        # 表单字段
        fields = [("商品编号：", "product_id"), ("商品名称：", "name"), ("商品分类：", "category"), ("单价（元）：", "price"), ("库存数量：", "stock")]
        self.form_vars = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text, font=("宋体", 12)).grid(row=i, column=0, sticky=tk.E, padx=10, pady=10)
            var = tk.StringVar()
            self.form_vars[var_name] = var
            entry = ttk.Entry(form_frame, textvariable=var, font=("宋体", 12), width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)

        # 提交按钮
        ttk.Button(self.content_frame, text="添加", command=self.add_product_submit).pack(pady=10)

    def add_product_submit(self):
        # 获取表单数据
        product_id = self.form_vars["product_id"].get().strip()
        name = self.form_vars["name"].get().strip()
        category = self.form_vars["category"].get().strip()
        price = self.form_vars["price"].get().strip()
        stock = self.form_vars["stock"].get().strip()

        # 调用原有添加商品逻辑
        success, msg = mall_system.add_product(product_id, name, category, price, stock)
        if success:
            messagebox.showinfo("成功", msg)
            # 清空表单
            for var in self.form_vars.values():
                var.set("")
        else:
            messagebox.showerror("失败", msg)

    def show_view_products(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="所有商品信息", font=("宋体", 16)).pack(pady=10)

        # 获取商品数据
        products = mall_system.get_all_products()
        if not products:
            ttk.Label(self.content_frame, text="系统中暂无商品信息！", font=("宋体", 12)).pack(pady=20)
            return

        # 创建表格
        columns = ("商品编号", "商品名称", "分类", "单价（元）", "库存", "总价值（元）")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)

        # 设置表头
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # 填充数据
        for product in products:
            tree.insert("", tk.END, values=(
                product.product_id, product.name, product.category,
                round(product.price, 2), product.stock, product.total_value
            ))

        # 滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_delete_product(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="删除商品信息", font=("宋体", 16)).pack(pady=10)

        # 商品编号输入
        ttk.Label(self.content_frame, text="请输入商品编号：", font=("宋体", 12)).pack(pady=10)
        self.delete_id_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.delete_id_var, font=("宋体", 12), width=30).pack(pady=5)

        # 删除按钮
        ttk.Button(self.content_frame, text="删除", command=self.delete_product_submit).pack(pady=10)

    def delete_product_submit(self):
        product_id = self.delete_id_var.get().strip()
        if not product_id:
            messagebox.showwarning("警告", "商品编号不能为空！")
            return

        if messagebox.askyesno("确认", f"确定要删除商品{product_id}吗？"):
            success, msg = mall_system.delete_product(product_id)
            if success:
                messagebox.showinfo("成功", msg)
                self.delete_id_var.set("")
            else:
                messagebox.showerror("失败", msg)

    def show_modify_product(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="修改商品信息", font=("宋体", 16)).pack(pady=10)

        # 商品编号输入
        ttk.Label(self.content_frame, text="请输入商品编号：", font=("宋体", 12)).pack(pady=10)
        self.modify_id_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.modify_id_var, font=("宋体", 12), width=30).pack(pady=5)
        ttk.Button(self.content_frame, text="查询商品", command=self.query_product_for_modify).pack(pady=5)

        # 修改字段区域（默认隐藏）
        self.modify_field_frame = ttk.Frame(self.content_frame)
        self.modify_field_var = tk.StringVar(value="name")
        self.modify_new_var = tk.StringVar()

    def query_product_for_modify(self):
        product_id = self.modify_id_var.get().strip()
        if not product_id:
            messagebox.showwarning("警告", "商品编号不能为空！")
            return

        # 查找商品
        product = next((p for p in mall_system.get_all_products() if p.product_id == product_id), None)
        if not product:
            messagebox.showerror("失败", "商品不存在！")
            return

        # 显示修改字段区域
        self.modify_field_frame.pack(pady=10)
        ttk.Label(self.modify_field_frame, text="选择修改字段：", font=("宋体", 12)).grid(row=0, column=0, padx=10, pady=10)
        fields = [("商品名称", "name"), ("商品分类", "category"), ("单价", "price"), ("库存", "stock")]
        for i, (text, value) in enumerate(fields):
            ttk.Radiobutton(self.modify_field_frame, text=text, variable=self.modify_field_var, value=value).grid(row=0, column=i+1, padx=5)

        ttk.Label(self.modify_field_frame, text="新值：", font=("宋体", 12)).grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self.modify_field_frame, textvariable=self.modify_new_var, font=("宋体", 12), width=30).grid(row=1, column=1, columnspan=4, padx=10, pady=10)

        ttk.Button(self.modify_field_frame, text="提交修改", command=lambda: self.modify_product_submit(product_id)).grid(row=2, column=0, columnspan=5, pady=10)

    def modify_product_submit(self, product_id):
        field = self.modify_field_var.get()
        new_value = self.modify_new_var.get().strip()
        if not new_value:
            messagebox.showwarning("警告", "新值不能为空！")
            return

        success, msg = mall_system.modify_product(product_id, field, new_value)
        if success:
            messagebox.showinfo("成功", msg)
            self.modify_new_var.set("")
        else:
            messagebox.showerror("失败", msg)

    # ------------------------------ 订单管理功能界面 ------------------------------
    def show_create_order(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="创建用户订单", font=("宋体", 16)).pack(pady=10)

        # 表单框架
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(pady=20)

        # 表单字段
        fields = [("订单编号：", "order_id"), ("用户手机号：", "phone"), ("商品编号：", "product_id"), ("购买数量：", "buy_count")]
        self.order_form_vars = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text, font=("宋体", 12)).grid(row=i, column=0, sticky=tk.E, padx=10, pady=10)
            var = tk.StringVar()
            self.order_form_vars[var_name] = var
            entry = ttk.Entry(form_frame, textvariable=var, font=("宋体", 12), width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)

        # 提交按钮
        ttk.Button(self.content_frame, text="创建订单", command=self.create_order_submit).pack(pady=10)

    def create_order_submit(self):
        order_id = self.order_form_vars["order_id"].get().strip()
        phone = self.order_form_vars["phone"].get().strip()
        product_id = self.order_form_vars["product_id"].get().strip()
        buy_count = self.order_form_vars["buy_count"].get().strip()

        success, msg = mall_system.create_order(order_id, phone, product_id, buy_count)
        if success:
            messagebox.showinfo("成功", msg)
            for var in self.order_form_vars.values():
                var.set("")
        else:
            messagebox.showerror("失败", msg)

    def show_query_order(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="查询订单信息", font=("宋体", 16)).pack(pady=10)

        # 订单编号输入
        ttk.Label(self.content_frame, text="请输入订单编号：", font=("宋体", 12)).pack(pady=10)
        self.query_order_id_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.query_order_id_var, font=("宋体", 12), width=30).pack(pady=5)
        ttk.Button(self.content_frame, text="查询", command=self.query_order_submit).pack(pady=10)

        # 订单详情显示区域
        self.order_detail_text = st.ScrolledText(self.content_frame, width=80, height=10, font=("宋体", 12))
        self.order_detail_text.pack(pady=10)

    def query_order_submit(self):
        order_id = self.query_order_id_var.get().strip()
        if not order_id:
            messagebox.showwarning("警告", "订单编号不能为空！")
            return

        order = mall_system.get_order(order_id)
        products = mall_system.get_all_products()
        if not order:
            self.order_detail_text.insert(tk.END, "订单不存在！")
            return

        # 查找商品名称
        product = next((p for p in products if p.product_id == order.product_id), None)
        product_name = product.name if product else "未知商品"

        # 显示详情
        detail = f"""订单编号：{order.order_id}
用户手机号：{order.phone}
商品信息：{product_name}（编号：{order.product_id}）
购买数量：{order.buy_count}
下单单价：{order.product_price:.2f} 元
订单总金额：{order.total_amount:.2f} 元
下单时间：{order.create_time.strftime('%Y-%m-%d %H:%M:%S')}"""
        self.order_detail_text.delete(1.0, tk.END)
        self.order_detail_text.insert(tk.END, detail)

    def show_cancel_order(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="撤销订单", font=("宋体", 16)).pack(pady=10)

        # 订单编号输入
        ttk.Label(self.content_frame, text="请输入订单编号：", font=("宋体", 12)).pack(pady=10)
        self.cancel_order_id_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.cancel_order_id_var, font=("宋体", 12), width=30).pack(pady=5)
        ttk.Button(self.content_frame, text="撤销", command=self.cancel_order_submit).pack(pady=10)

    def cancel_order_submit(self):
        order_id = self.cancel_order_id_var.get().strip()
        if not order_id:
            messagebox.showwarning("警告", "订单编号不能为空！")
            return

        if messagebox.askyesno("确认", f"确定要撤销订单{order_id}吗？（将恢复商品库存）"):
            success, msg = mall_system.cancel_order(order_id)
            if success:
                messagebox.showinfo("成功", msg)
                self.cancel_order_id_var.set("")
            else:
                messagebox.showerror("失败", msg)

    # ------------------------------ 其他功能 ------------------------------
    def show_statistics(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="订单统计分析", font=("宋体", 16)).pack(pady=10)

        # 获取统计数据
        stats = mall_system.get_order_statistics()
        if not stats:
            ttk.Label(self.content_frame, text="暂无订单数据，无法统计！", font=("宋体", 12)).pack(pady=20)
            return

        # 创建表格
        columns = ("商品分类", "销售数量", "销售总额（元）")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        # 填充数据
        total_count = 0
        total_amount = 0.0
        for category, data in stats.items():
            count = int(data["sales_count"])
            amount = round(data["sales_amount"], 2)
            tree.insert("", tk.END, values=(category, count, amount))
            total_count += count
            total_amount += amount

        # 总计行
        tree.insert("", tk.END, values=("总计", total_count, round(total_amount, 2)))

        # 滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def backup_data(self):
        if messagebox.askyesno("确认", "确定要手动备份数据吗？（将覆盖现有备份）"):
            success, msg = mall_system.backup_system_data()
            if success:
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("失败", msg)

    def restore_data(self):
        if messagebox.askyesno("确认", "确定要从备份恢复数据吗？（将覆盖当前数据）"):
            success, msg = mall_system.restore_system_data()
            if success:
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("失败", msg)

    def show_logs(self):
        # 清空内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(self.content_frame, text="系统日志（最近10条）", font=("宋体", 16)).pack(pady=10)

        # 关键词输入
        ttk.Label(self.content_frame, text="查询关键词（可选）：", font=("宋体", 12)).pack(pady=5)
        self.log_keyword_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.log_keyword_var, font=("宋体", 12), width=30).pack(pady=5)
        ttk.Button(self.content_frame, text="查询", command=self.query_logs_submit).pack(pady=5)

        # 日志显示区域
        self.log_text = st.ScrolledText(self.content_frame, width=80, height=15, font=("宋体", 10))
        self.log_text.pack(pady=10)

    def query_logs_submit(self):
        keyword = self.log_keyword_var.get().strip()
        logs = mall_system.get_recent_logs(keyword)
        self.log_text.delete(1.0, tk.END)
        for i, log in enumerate(logs, 1):
            self.log_text.insert(tk.END, f"{i}. {log}\n")

    def clear_logs(self):
        if messagebox.askyesno("确认", "确定要清理系统日志吗？（日志将永久删除）"):
            success, msg = mall_system.clear_logs()
            if success:
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("失败", msg)

    def exit_system(self):
        if messagebox.askyesno("确认", "确定要退出系统吗？"):
            mall_system.exit_system()
            self.root.destroy()

# 启动界面
if __name__ == "__main__":
    root = tk.Tk()
    app = MallGUI(root)
    root.mainloop()