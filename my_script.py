# -*-coding:utf-8 -*-
import requests
import json
import time
import os

# 配置常量
CONFIG_FILE = "deploy_history.json"
API_URL = "https://api.containers.back4app.com"
EXPIRATION_WINDOW = 3300  # 55分钟 (55 * 60)，留5分钟缓冲

HEADERS = {
    "Content-type": "application/json",
    "Cookie": "connect.sid=s%3AA8_6Za8WxhjthEfXxt4Mu7V32KxLFp_l.jclDua7AfdfeiC%2BNLVhs%2BgSCIK1zumHGF4Rscj%2BK%2FqU; __zlcmid=1X5oRJiNg0c7lcK; _gcl_au=1.1.687420229.1776323991; landingPage=%7B%22origin%22%3A%22https%3A%2F%2Fwww.back4app.com%22%2C%22host%22%3A%22www.back4app.com%22%2C%22pathname%22%3A%22%2F%22%7D; _ga=GA1.1.1303555323.1776323991; ab-XjkrUHOQKm=imMIQZ1JXS!0; b4a_amplitude_device_id=hIfcsXOgJyax6wd11KpPE6; mp_c6a824c901de2d494f8f060d6753e1ae_mixpanel=%7B%22distinct_id%22%3A%22%24device%3A7ad6a89a-87aa-40bb-bc4e-d42ff423b06e%22%2C%22%24device_id%22%3A%227ad6a89a-87aa-40bb-bc4e-d42ff423b06e%22%2C%22%24initial_referrer%22%3A%22%24direct%22%2C%22%24initial_referring_domain%22%3A%22%24direct%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%22%24initial_referrer%22%3A%22%24direct%22%2C%22%24initial_referring_domain%22%3A%22%24direct%22%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%7D; AMP_MKTG_bf3379918c=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRmRhc2hib2FyZC5iYWNrNGFwcC5jb20lMkYlMjIlMkMlMjJyZWZlcnJpbmdfZG9tYWluJTIyJTNBJTIyZGFzaGJvYXJkLmJhY2s0YXBwLmNvbSUyMiU3RA==; __gtm_referrer=https%3A%2F%2Fdashboard.back4app.com%2F; _rdt_uuid=1776323991045.0a29182e-3aa9-4b31-9e4f-d83a6d157d9b; _rdt_pn=:150~8d32f9b7dc1bdcebaddabd59c27efb24cec1da5b3c8738ceae56db1f160e8700|150~404416762d726ed40f46eeb53552e407a3e8390151a83374462d6d3deb5c9470|150~b48b062baddb53462fd79099007cbfccc3b049bea677b90ee420e32cb7db7c3f|125~7e071fd9b023ed8f18458a73613a0834f6220bd5cc50357ba3493c6040a9ea8c|125~b8acd28c3c3bb84619df1bcc5a56799ad5d375ce825c38f4f9e31e2c918a5372; _rdt_em=:f0944b6c79674d0478dff88a835bcf0079243d35f5faf91adf2bba1db1b06cf7,0f1f9d9d80e0e0137467151dea38eba8ca72f64fa6d370fdce72982c858384cb,66f715b25f0bc8c892870332a9ce0af5a48df44b289c215a1d2af764c537e2fa,36ea61d0bfcdd5ab7c2d47c82e0ca365ab258ebac36edfd51b035a05cfe9e789,b44729b0570e6310772864b785fdb6a5260920af435c532f1e51a6a7e180d6d3; _ga_FJK5KX97E0=GS2.1.s1776389642$o5$g1$t1776391657$j60$l0$h683219038; amp_bf3379_back4app.com=hIfcsXOgJyax6wd11KpPE6...1jmch5rhc.1jmcj4e63.2k.2.2m; AMP_bf3379918c=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJoSWZjc1hPZ0p5YXg2d2QxMUtwUEU2JTIyJTJDJTIydXNlcklkJTIyJTNBJTIyeWVhcm9mdGhlcmFpbiU0MHFxLmNvbSUyMiUyQyUyMnNlc3Npb25JZCUyMiUzQTE3NzYzOTAzMDkyNTUlMkMlMjJvcHRPdXQlMjIlM0FmYWxzZSUyQyUyMmxhc3RFdmVudFRpbWUlMjIlM0ExNzc2MzkxNjk4NjMxJTdE"
}

# 应用映射
APP_ID_MAP = {
    "35899a9a-d97d-4f57-92cc-272b0acfe51c": "f4b1b025-deef-xxxx"
}

def load_history():
    """从本地文件加载部署历史"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(history):
    """保存部署历史到本地"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(history, f)

def list_apps():
    query = {
        "query": "query Apps { apps { id name mainService { repository { fullName } mainServiceEnvironment { mainCustomDomain { status } } } } }"
    }
    try:
        res = requests.post(API_URL, json=query, headers=HEADERS, timeout=10)
        res.raise_for_status()
        apps = res.json().get("data", {}).get("apps", [])
        
        status_list = []
        for app in apps:
            status_list.append({
                "app_id": app["id"],
                "app_name": app["mainService"]['repository']['fullName'],
                "domain_status": app["mainService"]["mainServiceEnvironment"]["mainCustomDomain"]["status"]
            })
        return status_list
    except Exception as e:
        print(f"获取应用列表失败: {e}")
        return []

def trigger_deploy(app_id):
    service_env_id = APP_ID_MAP.get(app_id)
    if not service_env_id:
        return False

    payload = {
        "operationName": "triggerManualDeployment",
        "variables": {"serviceEnvironmentId": service_env_id},
        "query": "mutation triggerManualDeployment($serviceEnvironmentId: String!) { triggerManualDeployment(serviceEnvironmentId: $serviceEnvironmentId) { id status } }"
    }
    
    try:
        res = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
        if res.status_code == 200 and "error" not in res.text:
            return True
    except Exception as e:
        print(f"触发部署异常: {e}")
    return False

def auto_redeploy():
    history = load_history()
    current_time = time.time()
    apps = list_apps()
    
    for app in apps:
        app_id = app["app_id"]
        app_name = app["app_name"]
        last_deploy = history.get(app_id, 0)
        
        # 逻辑判断：
        # 1. 距离上次部署是否不满 55 分钟？如果是，直接跳过，不调 API 检查具体状态
        if current_time - last_deploy < EXPIRATION_WINDOW:
            minutes_left = int((EXPIRATION_WINDOW - (current_time - last_deploy)) / 60)
            print(f"-> {app_name}: 部署尚在有效期内，约 {minutes_left} 分钟后重新评估")
            continue

        # 2. 如果超过 55 分钟，检查 API 状态
        if app["domain_status"] == "EXPIRED":
            if app_id not in APP_ID_MAP:
                print(f"! {app_name}: 缺少 serviceEnvId 映射")
                continue
            
            print(f"* {app_name}: 域名已过期，执行重新部署...")
            if trigger_deploy(app_id):
                history[app_id] = time.time()
                print(f"√ {app_name}: 部署指令发送成功")
            else:
                print(f"× {app_name}: 部署失败")
        else:
            # 域名虽然过了55分钟但还没显示 EXPIRED，更新一下时间，避免频繁请求
            print(f"-> {app_name}: 状态正常 ({app['domain_status']})")
            
    save_history(history)

if __name__ == '__main__':
    auto_redeploy()
