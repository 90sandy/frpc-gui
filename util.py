import tkinter as tk


def validate_ip_address(ip):
    """
    验证 IP 地址格式
    支持 IPv4 地址
    
    参数:
        ip: IP 地址字符串
    
    返回:
        bool: 是否为有效的 IPv4 地址
    """
    if not ip or not isinstance(ip, str):
        return False
    
    # IPv4 地址格式验证
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except ValueError:
        return False


def validate_port(port, min_port=1, max_port=65535):
    """
    验证端口号是否在有效范围内
    
    参数:
        port: 端口号（可以是字符串或整数）
        min_port: 最小端口号，默认 1
        max_port: 最大端口号，默认 65535
    
    返回:
        (is_valid, port_int): (是否有效, 端口整数)
    """
    try:
        port_int = int(port)
        if min_port <= port_int <= max_port:
            return True, port_int
        else:
            return False, port_int
    except (ValueError, TypeError):
        return False, None


def center_window(window):
    """
    将窗口居中显示在屏幕上
    
    参数:
        window: Tkinter 窗口对象
    """
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
    y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
    window.geometry(f"+{x}+{y}")
