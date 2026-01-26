import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from setting import check_frpc_config, show_settings_window, get_frpc_exe_path
from proxy import ProxyManager


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FRPC 客户端")
        self.root.geometry("800x600")
        
        # 居中显示窗口
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # 创建主容器
        main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧菜单栏
        self.menu_frame = ttk.Frame(main_container, width=200)
        main_container.add(self.menu_frame, weight=0)
        
        # 右侧内容区域
        self.content_frame = ttk.Frame(main_container)
        main_container.add(self.content_frame, weight=1)
        
        # 初始化菜单
        self.init_menu()
        
        # 初始化内容区域
        self.current_page = None
        self.frpc_process = None  # FRPC 进程对象
        self.auto_refresh_id = None  # 自动刷新定时器 ID
        
        # 初始化代理管理器
        self.proxy_manager = ProxyManager(self.root, self.content_frame, self.refresh_proxy_callback)
        
        self.show_status_page()
        
        # 绑定窗口关闭事件，确保进程被清理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def refresh_proxy_callback(self):
        """代理刷新回调"""
        if hasattr(self, 'proxy_manager'):
            self.proxy_manager.refresh_proxy_list()
    
    def init_menu(self):
        """初始化左侧菜单"""
        # 菜单标题
        title_label = ttk.Label(
            self.menu_frame,
            text="FRPC 客户端",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=20)
        
        # 分隔线
        ttk.Separator(self.menu_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        
        # 菜单按钮
        menu_items = [
            ("服务", self.show_status_page),
            ("代理", self.show_proxy_page),
            ("日志", self.show_log_page),
            ("设置", self.show_settings_page),
        ]
        
        self.menu_buttons = []
        for i, (text, command) in enumerate(menu_items):
            btn = ttk.Button(
                self.menu_frame,
                text=text,
                command=command,
                width=20
            )
            btn.pack(pady=5, padx=10, fill=tk.X)
            self.menu_buttons.append(btn)
        
        # 初始化时，如果服务未启动，禁用代理菜单按钮
        self.update_proxy_menu_state()
    
    def clear_content(self):
        """清空右侧内容区域"""
        # 停止自动刷新
        self.stop_auto_refresh()
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_status_page(self):
        """显示状态页面"""
        self.clear_content()
        self.current_page = "status"
        
        # 更新菜单按钮状态
        self.update_menu_highlight(0)
        
        # 状态页面内容
        status_frame = ttk.Frame(self.content_frame, padding="20")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            status_frame,
            text="服务状态",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # 状态信息区域
        info_frame = ttk.LabelFrame(status_frame, text="状态信息", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 状态显示
        self.status_label = ttk.Label(
            info_frame,
            text="状态: 未启动",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
        
        # 按钮区域
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(pady=30)
        
        # 启动按钮
        self.start_button = ttk.Button(
            button_frame,
            text="启动",
            command=self.start_frpc,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_frpc,
            width=15,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
    
    def show_proxy_page(self):
        """显示代理页面"""
        # 检查服务是否已启动
        if not self.is_service_running():
            messagebox.showwarning("提示", "请先启动 FRPC 服务")
            # 切换到服务页面
            self.show_status_page()
            return
        
        self.clear_content()
        self.current_page = "proxy"
        
        # 更新菜单按钮状态
        self.update_menu_highlight(1)
        
        # 使用代理管理器显示代理页面
        self.proxy_manager.show_proxy_page()
    
    def show_log_page(self):
        """显示日志页面"""
        self.clear_content()
        self.current_page = "log"
        
        # 更新菜单按钮状态
        self.update_menu_highlight(2)
        
        # 日志页面内容
        log_frame = ttk.Frame(self.content_frame, padding="20")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题和按钮区域
        header_frame = ttk.Frame(log_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="运行日志",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # 刷新按钮
        refresh_button = ttk.Button(
            header_frame,
            text="刷新",
            command=self.refresh_log,
            width=10
        )
        refresh_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 日志显示区域
        log_text_frame = ttk.LabelFrame(log_frame, text="日志内容", padding="10")
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用 ScrolledText 显示日志
        self.log_text = scrolledtext.ScrolledText(
            log_text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#d4d4d4",
            state=tk.DISABLED  # 只读模式
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始加载日志
        self.refresh_log()
        
        # 设置定时刷新（每2秒自动刷新一次）
        self.auto_refresh_id = None
        self.start_auto_refresh()
    
    def refresh_log(self):
        """刷新日志内容"""
        # 检查日志文本区域是否存在
        if not hasattr(self, 'log_text') or self.log_text is None:
            return
        
        log_file = 'frpc.log'
        
        try:
            # 启用文本区域进行编辑
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self.log_text.insert(tk.END, content)
                except Exception as e:
                    self.log_text.insert(tk.END, f"读取日志文件失败: {str(e)}\n")
            else:
                self.log_text.insert(tk.END, "日志文件不存在: frpc.log\n")
                self.log_text.insert(tk.END, "请确保 FRPC 服务已启动并配置了日志输出。\n")
            
            # 禁用文本区域（只读模式）
            self.log_text.config(state=tk.DISABLED)
            
            # 自动滚动到底部
            self.log_text.see(tk.END)
        except Exception as e:
            # 如果出错，尝试恢复只读状态
            try:
                self.log_text.config(state=tk.DISABLED)
            except:
                pass
    
    def start_auto_refresh(self):
        """启动自动刷新"""
        # 只在日志页面时刷新
        if hasattr(self, 'current_page') and self.current_page == "log":
            self.refresh_log()
            # 每2秒刷新一次
            self.auto_refresh_id = self.root.after(2000, self.start_auto_refresh)
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self.auto_refresh_id:
            self.root.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None
    
    def show_settings_page(self):
        """显示设置页面 - 打开设置窗口"""
        # 更新菜单按钮状态
        self.update_menu_highlight(3)
        
        # 直接调用 setting.py 中的设置窗口（支持父窗口）
        show_settings_window(self.root)
    
    def update_menu_highlight(self, active_index):
        """更新菜单按钮高亮状态"""
        for i, btn in enumerate(self.menu_buttons):
            if i == active_index:
                btn.configure(style="Accent.TButton")
            else:
                btn.configure(style="TButton")
    
    def is_service_running(self):
        """检查服务是否正在运行"""
        if self.frpc_process is None:
            return False
        return self.frpc_process.poll() is None
    
    def update_proxy_menu_state(self):
        """更新代理菜单按钮的启用/禁用状态"""
        if len(self.menu_buttons) > 1:
            proxy_button = self.menu_buttons[1]  # 代理按钮是第二个（索引为1）
            if self.is_service_running():
                proxy_button.config(state=tk.NORMAL)
            else:
                proxy_button.config(state=tk.DISABLED)
    
    def start_frpc(self):
        """启动 FRPC 服务"""
        try:
            # 检查配置文件是否存在
            if not os.path.exists('frpc.toml'):
                messagebox.showerror("错误", "未找到 frpc.toml 配置文件")
                return
            
            # 获取 frpc.exe 路径
            frpc_exe_path = get_frpc_exe_path()
            if not frpc_exe_path or not os.path.exists(frpc_exe_path):
                messagebox.showerror("错误", "未找到 frpc.exe 文件，请在设置中配置路径")
                return
            
            # 检查进程是否已经在运行
            if self.frpc_process is not None:
                # 检查进程是否还在运行
                if self.frpc_process.poll() is None:
                    messagebox.showwarning("提示", "FRPC 服务已在运行中")
                    return
                else:
                    # 进程已结束，清理引用
                    self.frpc_process = None
            
            # 启动 FRPC 进程
            # 使用 subprocess.Popen 启动，不显示控制台窗口
            self.frpc_process = subprocess.Popen(
                [frpc_exe_path, '-c', 'frpc.toml'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # 更新 UI
            self.status_label.config(text="状态: 运行中")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 启用代理菜单按钮
            self.update_proxy_menu_state()
            
            messagebox.showinfo("成功", "FRPC 服务已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动 FRPC 服务失败：{str(e)}")
            if self.frpc_process:
                self.frpc_process = None
            self.status_label.config(text="状态: 启动失败")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_frpc(self):
        """停止 FRPC 服务"""
        try:
            if self.frpc_process is None:
                messagebox.showwarning("提示", "FRPC 服务未运行")
                return
            
            # 检查进程是否还在运行
            if self.frpc_process.poll() is None:
                # 进程还在运行，终止它
                self.frpc_process.terminate()
                
                # 等待进程结束，最多等待 5 秒
                try:
                    self.frpc_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 如果进程没有响应，强制杀死
                    self.frpc_process.kill()
                    self.frpc_process.wait()
            else:
                # 进程已经结束
                pass
            
            # 清理进程引用
            self.frpc_process = None
            
            # 更新 UI
            self.status_label.config(text="状态: 已停止")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # 禁用代理菜单按钮
            self.update_proxy_menu_state()
            
            # 如果当前在代理页面，切换回服务页面
            if self.current_page == "proxy":
                self.show_status_page()
            
            messagebox.showinfo("成功", "FRPC 服务已停止")
            
        except Exception as e:
            messagebox.showerror("错误", f"停止 FRPC 服务失败：{str(e)}")
            # 即使出错也清理引用
            self.frpc_process = None
            self.status_label.config(text="状态: 已停止")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def on_closing(self):
        """窗口关闭时的处理"""
        # 停止自动刷新
        self.stop_auto_refresh()
        
        # 如果进程还在运行，先停止它
        if self.frpc_process is not None and self.frpc_process.poll() is None:
            try:
                self.frpc_process.terminate()
                try:
                    self.frpc_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.frpc_process.kill()
                    self.frpc_process.wait()
            except:
                pass
            self.frpc_process = None
        
        # 关闭窗口
        self.root.destroy()


def show_main_window():
    """显示主窗口"""
    if not check_frpc_config():
        return False
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    return True


if __name__ == '__main__':
    show_main_window()
