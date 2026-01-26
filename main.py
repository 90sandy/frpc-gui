"""
FRPC 桌面客户端
"""
from setting import init_frpc_config
from service import show_main_window


if __name__ == '__main__':
    # 初始化配置，如果不存在则显示设置窗口
    if init_frpc_config():
        # 配置文件存在，显示主窗口
        show_main_window()
    else:
        # 配置文件已生成，再次检查并显示主窗口
        if init_frpc_config():
            show_main_window()
