# -*- coding: utf-8 -*-
"""
WPS 金山文档开放平台 —— 连通性测试脚本（只读，不写任何数据，安全）

用途：
    拿到「应用ID / 应用密钥 / 文件ID」之后，先跑这个脚本，
    验证 API 权限是否开通、能不能访问到你的表格。

前提：
    1. 已在开放平台创建并【发布】企业自建应用
    2. 已在「权限管理」里申请了表格相关权限
    3. 本机已安装 Python3 并 pip install requests

用法：
    填好下面的配置区，然后在命令行运行：
        python wps_api_smoke_test.py
"""

import json
import requests

# ==================== 配置区：把你准备的东西填在这里 ====================
应用ID   = "AKxxxxxxxxxx"   # 开放平台「应用信息」里的 应用ID
应用密钥 = "xxxxxxxxxx"     # 开放平台「应用信息」里的 应用密钥
文件ID   = "xxxxxxxxxx"     # 右键表格标签 -> 文档信息 -> 文件ID
# =======================================================================

TOKEN_URL = "https://openapi.wps.cn/oauth2/token"
API_BASE  = "https://openapi.wps.cn/v7/airsheet"   # 智能表格/多维表格的路径


def 获取访问令牌():
    """用 应用ID + 密钥 换 access_token（相当于临时通行证）"""
    r = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": 应用ID,
            "client_secret": 应用密钥,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def 列出工作表(令牌):
    """读取该文件里的工作表列表，返回原始 JSON"""
    r = requests.get(
        f"{API_BASE}/{文件ID}/worksheets",
        headers={"Authorization": f"Bearer {令牌}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("① 正在获取 access_token ...")
    令牌 = 获取访问令牌()
    print("   ✅ 令牌获取成功\n")

    print("② 正在读取工作表列表 ...")
    数据 = 列出工作表(令牌)
    print("   ✅ 接口调用成功！以下是返回内容：\n")
    print(json.dumps(数据, ensure_ascii=False, indent=2))

    print("\n如果能看到工作表名称和 sheet_id，说明 API 已完全打通，可以进入正式开发。")
