import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
import urllib3
from datetime import datetime

# 禁用SSL证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ACLRealTimeSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网闸ACL实时搜索工具")
        self.root.geometry("1300x750")
        self.root.resizable(True, True)
        
        # 初始化网闸地址（空值，由用户配置）
        self.BASE_URL = ""
        self.LOGIN_PAGE_URL = ""
        self.ACL_PAGE_URL = ""
        self.ACL_API_URL = ""
        
        # 状态变量
        self.is_logged_in = False
        self.session = requests.Session()
        self.acl_data = pd.DataFrame()
        self.config_window = None
        self.login_window = None
        
        # 第一步：先显示网闸地址配置窗口
        self._show_config_window()

    def _center_window(self, window):
        """窗口居中"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _show_config_window(self):
        """显示网闸地址配置窗口（解决无法自定义URL问题）"""
        # 销毁旧窗口
        if self.config_window and tk.Toplevel.winfo_exists(self.config_window):
            self.config_window.destroy()
        
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("网闸地址配置")
        self.config_window.geometry("450x350")
        self.config_window.resizable(False, False)
        self.config_window.grab_set()
        self._center_window(self.config_window)
        
        # 标题
        ttk.Label(self.config_window, text="网闸地址配置", font=("SimHei", 14, "bold")).pack(pady=10)
        ttk.Label(self.config_window, text="请输入目标网闸的IP/域名（无需https://）").pack(pady=5)
        
        # 网闸IP输入
        ip_frame = ttk.Frame(self.config_window)
        ip_frame.pack(fill=tk.X, padx=30, pady=10)
        ttk.Label(ip_frame, text="网闸IP/域名：").pack(side=tk.LEFT)
        self.gateway_ip = ttk.Entry(ip_frame, width=30)
        self.gateway_ip.pack(side=tk.LEFT, padx=5)
        
        # 端口输入（可选）
        port_frame = ttk.Frame(self.config_window)
        port_frame.pack(fill=tk.X, padx=30, pady=8)
        ttk.Label(port_frame, text="端口（默认443）：").pack(side=tk.LEFT)
        self.gateway_port = ttk.Entry(port_frame, width=30)
        self.gateway_port.pack(side=tk.LEFT, padx=5)
        self.gateway_port.insert(0, "443")
        
        # 高级配置（可选）
        ttk.Label(self.config_window, text="高级配置（默认无需修改）", font=("SimHei", 10, "bold")).pack(pady=8)
        
        # ACL接口路径
        api_frame = ttk.Frame(self.config_window)
        api_frame.pack(fill=tk.X, padx=30, pady=5)
        ttk.Label(api_frame, text="ACL接口路径：").pack(side=tk.LEFT)
        self.acl_api_path = ttk.Entry(api_frame, width=30)
        self.acl_api_path.pack(side=tk.LEFT, padx=5)
        self.acl_api_path.insert(0, "/jdwa/exchanger/aclPolicy")
        
        # 登录页路径
        login_path_frame = ttk.Frame(self.config_window)
        login_path_frame.pack(fill=tk.X, padx=30, pady=5)
        ttk.Label(login_path_frame, text="登录页路径：").pack(side=tk.LEFT)
        self.login_path = ttk.Entry(login_path_frame, width=30)
        self.login_path.pack(side=tk.LEFT, padx=5)
        self.login_path.insert(0, "/index.jsp")
        
        # ACL页面路径
        acl_path_frame = ttk.Frame(self.config_window)
        acl_path_frame.pack(fill=tk.X, padx=30, pady=5)
        ttk.Label(acl_path_frame, text="ACL页面路径：").pack(side=tk.LEFT)
        self.acl_path = ttk.Entry(acl_path_frame, width=30)
        self.acl_path.pack(side=tk.LEFT, padx=5)
        self.acl_path.insert(0, "/jsp/acl.jsp")
        
        # 按钮
        btn_frame = ttk.Frame(self.config_window)
        btn_frame.pack(pady=15)
        confirm_btn = ttk.Button(btn_frame, text="确认配置", command=self._confirm_config, width=12)
        confirm_btn.pack(side=tk.LEFT, padx=10)
        reset_btn = ttk.Button(btn_frame, text="重新配置", command=self._use_default_config, width=12)
        reset_btn.pack(side=tk.LEFT)

    def _confirm_config(self):
        """确认网闸地址配置"""
        ip = self.gateway_ip.get().strip()
        port = self.gateway_port.get().strip() or "443"
        acl_api_path = self.acl_api_path.get().strip()
        login_path = self.login_path.get().strip()
        acl_path = self.acl_path.get().strip()
        
        if not ip:
            messagebox.showwarning("提示", "网闸IP/域名不能为空！")
            return
        
        # 构建完整URL
        self.BASE_URL = f"https://{ip}:{port}"
        self.LOGIN_PAGE_URL = f"{self.BASE_URL}{login_path}"
        self.ACL_PAGE_URL = f"{self.BASE_URL}{acl_path}"
        self.ACL_API_URL = f"{self.BASE_URL}{acl_api_path}"
        
        # 关闭配置窗口，显示登录窗口
        if tk.Toplevel.winfo_exists(self.config_window):
            self.config_window.destroy()
        self._show_login_window()

    def _use_default_config(self):
        """使用默认配置"""
        # 不设置默认IP，需要用户手动输入
        if tk.Toplevel.winfo_exists(self.config_window):
            self.config_window.destroy()
        # 显示提示信息
        messagebox.showinfo("提示", "请在配置窗口中输入网闸IP/域名")
        self._show_config_window()

    def _show_login_window(self):
        """显示登录窗口（只保留Cookie登录）"""
        if self.login_window and tk.Toplevel.winfo_exists(self.login_window):
            self.login_window.destroy()
        
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title(f"网闸登录验证 - {self.BASE_URL}")
        self.login_window.geometry("450x280")
        self.login_window.resizable(False, False)
        self.login_window.grab_set()
        self._center_window(self.login_window)
        
        # 显示目标网闸地址
        ttk.Label(self.login_window, text=f"目标网闸：{self.BASE_URL}", foreground="blue").pack(pady=5)
        ttk.Label(self.login_window, text="Cookie登录（推荐）", font=("SimHei", 10, "bold")).pack(pady=8)
        ttk.Label(self.login_window, text="格式：JSESSIONID=xxx; other=xxx").pack()
        
        # Cookie输入
        cookie_frame = ttk.Frame(self.login_window)
        cookie_frame.pack(fill=tk.X, padx=30, pady=10)
        self.cookie_entry = ttk.Entry(cookie_frame, width=40)
        self.cookie_entry.pack(side=tk.LEFT)
        
        # 按钮区域
        btn_frame = ttk.Frame(self.login_window)
        btn_frame.pack(pady=20)
        cookie_btn = ttk.Button(btn_frame, text="Cookie登录", command=self._login_with_cookie, width=15)
        cookie_btn.pack(side=tk.LEFT, padx=10)
        test_btn = ttk.Button(btn_frame, text="测试连接", command=self._test_connection, width=15)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        # 回车触发Cookie登录
        self.login_window.bind("<Return>", lambda event: self._login_with_cookie())

    def _test_connection(self):
        """测试网闸连接"""
        try:
            resp = self.session.get(self.LOGIN_PAGE_URL, verify=False, timeout=10)
            if resp.status_code == 200:
                messagebox.showinfo("成功", "已成功连接到网闸！")
            else:
                messagebox.showerror("错误", f"连接失败，状态码：{resp.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("错误", "无法连接到网闸！请检查：\n1. IP/端口是否正确\n2. 网络是否可达\n3. 防火墙是否开放")
        except Exception as e:
            messagebox.showerror("错误", f"测试异常：{str(e)}")

    def _login_with_cookie(self):
        """Cookie登录（核心解决登录失败问题）"""
        cookie_str = self.cookie_entry.get().strip()
        if not cookie_str:
            messagebox.showwarning("提示", "请输入Cookie！")
            return
        
        try:
            # 解析Cookie字符串
            cookies = {}
            for item in cookie_str.split(";"):
                item = item.strip()
                if "=" in item:
                    key, value = item.split("=", 1)
                    cookies[key] = value
            
            # 导入Cookie到会话
            self.session.cookies.update(cookies)
            
            # 验证Cookie是否有效
            acl_resp = self.session.get(self.ACL_PAGE_URL, verify=False, timeout=10)
            if "登录" not in acl_resp.text:
                self.is_logged_in = True
                self.login_window.destroy()
                self._create_main_interface()
                self._fetch_acl_data()
                messagebox.showinfo("成功", "Cookie登录成功！已加载ACL数据")
            else:
                messagebox.showerror("错误", "Cookie无效！请重新复制登录后的Cookie")
        except Exception as e:
            messagebox.showerror("错误", f"Cookie登录失败：{str(e)}")

    def _create_main_interface(self):
        """创建主界面"""
        # 清除旧的界面元素，避免重复创建
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # ========== 顶部栏（显示当前网闸+重新配置+刷新） ==========
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text=f"当前网闸：{self.BASE_URL}", foreground="blue").pack(side=tk.LEFT, padx=5)
        config_btn = ttk.Button(top_frame, text="重新配置网闸地址", command=self._show_config_window, width=15)
        config_btn.pack(side=tk.LEFT, padx=10)
        refresh_btn = ttk.Button(top_frame, text="刷新ACL数据", command=self._fetch_acl_data)
        refresh_btn.pack(side=tk.LEFT, padx=10)
        export_btn = ttk.Button(top_frame, text="导出数据", command=self._export_data)
        export_btn.pack(side=tk.LEFT, padx=10)
        self.stat_label = ttk.Label(top_frame, text="数据状态：未加载 | 最后更新：-- | 总数：0")
        self.stat_label.pack(side=tk.LEFT, padx=20)
        
        # ========== 搜索区域 ==========
        search_frame = ttk.LabelFrame(self.root, text="搜索条件", padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="搜索字段：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.search_type = ttk.Combobox(search_frame, values=["名称", "客户端地址", "目的地址", "所属端机", "协议类型"], width=15)
        self.search_type.current(0)
        self.search_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_frame, text="关键词：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=3, padx=5, pady=5)
        self.search_entry.bind("<Return>", self._on_search)
        
        self.match_mode = tk.StringVar(value="模糊匹配")
        ttk.Radiobutton(search_frame, text="模糊匹配", variable=self.match_mode, value="模糊匹配").grid(row=0, column=4, padx=5, pady=5)
        ttk.Radiobutton(search_frame, text="精确匹配", variable=self.match_mode, value="精确匹配").grid(row=0, column=5, padx=5, pady=5)
        
        search_btn = ttk.Button(search_frame, text="搜索", command=self._on_search, width=8)
        search_btn.grid(row=0, column=6, padx=5, pady=5)
        clear_btn = ttk.Button(search_frame, text="清空", command=self._clear_search, width=8)
        clear_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # ========== 数据表格 ==========
        result_frame = ttk.LabelFrame(self.root, text="ACL数据列表", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(result_frame, show="headings", height=20)
        self.columns = ["序号", "名称", "所属端机", "控制模式", "监控网卡",
                        "协议类型", "动作", "客户端地址", "客户端掩码", "客户端端口段",
                        "目的地址", "目的地址掩码", "目的端口段", "启停按钮"]
        self.tree["columns"] = self.columns
        
        column_widths = [60, 100, 100, 80, 80, 80, 60, 120, 100, 100, 120, 100, 100, 80]
        for col, width in zip(self.columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # 滚动条
        vscroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hscroll = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vscroll.grid(row=0, column=1, sticky=tk.NS)
        hscroll.grid(row=1, column=0, sticky=tk.EW)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

    def _fetch_acl_data(self):
        """加载ACL数据"""
        self.stat_label.config(text="数据状态：正在加载... | 最后更新：-- | 总数：0")
        self.root.update()
        
        try:
            acl_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "Referer": self.ACL_PAGE_URL,
                "X-Requested-With": "XMLHttpRequest"
            }
            
            response = self.session.get(
                self.ACL_API_URL,
                headers=acl_headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            # 容错解析
            try:
                raw_data = response.json()
            except ValueError:
                # 如果不是JSON，尝试从ACL页面提取（简单适配）
                messagebox.showwarning("提示", "ACL接口返回非JSON数据，尝试从页面提取...")
                raw_data = []
                # 这里可以根据实际页面结构补充解析逻辑
                self.stat_label.config(text="数据状态：接口异常 | 最后更新：-- | 总数：0")
                return
            
            # 处理数据
            if not raw_data:
                messagebox.showinfo("提示", "未获取到ACL数据！")
                self.stat_label.config(text="数据状态：无数据 | 最后更新：-- | 总数：0")
                return
            
            self.acl_data = pd.DataFrame(raw_data).drop_duplicates(subset='id', keep='first')
            field_mapping = {
                "id": "序号", "name": "名称", "nodeId": "所属端机", "aclTypeName": "控制模式",
                "dev": "监控网卡", "appType": "协议类型", "status": "动作",
                "clientIp": "客户端地址", "clientMask": "客户端掩码", "clientPortSeg": "客户端端口段",
                "dstIp": "目的地址", "dstMask": "目的地址掩码", "dstPortSeg": "目的端口段", "filter_type": "启停按钮"
            }
            # 只保留存在的列
            for col in list(self.acl_data.columns):
                if col not in field_mapping:
                    self.acl_data.drop(col, axis=1, inplace=True)
            self.acl_data.rename(columns=field_mapping, inplace=True)
            
            # 动作转换
            if "动作" in self.acl_data.columns:
                self.acl_data["动作"] = self.acl_data["动作"].map({True: "允许", False: "拒绝", 1: "允许", 0: "拒绝"})
            
            # 填充表格
            self._clear_tree()
            for idx, row in self.acl_data.iterrows():
                row_data = []
                for col in self.columns:
                    val = row.get(col, "")
                    row_data.append(str(val) if pd.notna(val) else "")
                self.tree.insert("", tk.END, values=row_data)
            
            # 更新状态
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stat_label.config(text=f"数据状态：加载完成 | 最后更新：{update_time} | 总数：{len(self.acl_data)}")
            
        except requests.exceptions.ConnectionError:
            self.stat_label.config(text="数据状态：连接失败 | 最后更新：-- | 总数：0")
            messagebox.showerror("错误", "无法连接到ACL接口！")
        except Exception as e:
            self.stat_label.config(text="数据状态：加载失败 | 最后更新：-- | 总数：0")
            messagebox.showerror("错误", f"加载失败：{str(e)}")

    def _on_search(self, event=None):
        """执行搜索"""
        if self.acl_data.empty:
            messagebox.showwarning("提示", "请先刷新加载ACL数据！")
            return
        
        search_field = self.search_type.get()
        keyword = self.search_entry.get().strip()
        match_mode = self.match_mode.get()
        
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词！")
            return
        
        self._clear_tree()
        try:
            if search_field not in self.acl_data.columns:
                messagebox.showwarning("提示", f"字段「{search_field}」不存在！")
                return
            
            if match_mode == "精确匹配":
                filtered_data = self.acl_data[self.acl_data[search_field].astype(str) == keyword]
            else:
                filtered_data = self.acl_data[self.acl_data[search_field].astype(str).str.contains(keyword, case=False, na=False)]
            
            # 填充结果
            for idx, row in filtered_data.iterrows():
                row_data = []
                for col in self.columns:
                    val = row.get(col, "")
                    row_data.append(str(val) if pd.notna(val) else "")
                self.tree.insert("", tk.END, values=row_data)
            
            # 更新状态
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stat_label.config(text=f"数据状态：搜索结果 | 最后更新：{update_time} | 匹配数：{len(filtered_data)}")
            
            if len(filtered_data) == 0:
                messagebox.showinfo("提示", "未找到匹配的ACL记录！")
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败：{str(e)}")

    def _clear_search(self):
        """清空搜索"""
        self.search_entry.delete(0, tk.END)
        self.search_type.current(0)
        self.match_mode.set("模糊匹配")
        
        self._clear_tree()
        if not self.acl_data.empty:
            for idx, row in self.acl_data.iterrows():
                row_data = []
                for col in self.columns:
                    val = row.get(col, "")
                    row_data.append(str(val) if pd.notna(val) else "")
                self.tree.insert("", tk.END, values=row_data)
            
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stat_label.config(text=f"数据状态：加载完成 | 最后更新：{update_time} | 总数：{len(self.acl_data)}")

    def _clear_tree(self):
        """清空表格"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _export_data(self):
        """导出ACL数据"""
        if self.acl_data.empty:
            messagebox.showwarning("提示", "没有数据可导出！")
            return
        
        try:
            # 生成导出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"acl_data_{timestamp}.xlsx"
            
            # 导出到Excel文件
            self.acl_data.to_excel(filename, index=False, engine='openpyxl')
            
            messagebox.showinfo("成功", f"数据已导出到文件：{filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

if __name__ == "__main__":
    # 自动安装依赖
    try:
        import requests, pandas
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pandas", "openpyxl"])
    
    # 启动GUI
    root = tk.Tk()
    app = ACLRealTimeSearchGUI(root)
    root.mainloop()