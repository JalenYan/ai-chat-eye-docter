from nacos import NacosException, NacosClient
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.config import settings
import time



NACOS_SERVER_ADDRESS = settings.nacos_server_address
NACOS_NAMESPACE = settings.nacos_namespace
NACOS_SERVICE_NAME = settings.nacos_service_name
NACOS_GROUP_NAME = settings.nacos_group_name
NACOS_PORT = settings.nacos_port
Local_IP = settings.local_ip

#服务器运行端口
Port = settings.port

# 初始化应用
def init_app():
    service_port = Port
    # 初始化Nacos客户端
    nacos_client = NacosClient(
        server_addresses=f"http://{NACOS_SERVER_ADDRESS}",  # 明确端口
        namespace=NACOS_NAMESPACE,
    )
    try:
        nacos_client.add_naming_instance(
            service_name=NACOS_SERVICE_NAME,
            ip=Local_IP,
            port=service_port,  # ✅ 每个端口单独注册
            group_name=NACOS_GROUP_NAME,
            metadata={
                "health_check_url": f"http://{Local_IP}:{service_port}/health",
                "cluster": "default"
            }
        )
        print(f"✅ 端口 {service_port} 注册成功")
    except NacosException as e:
        print(f"❌ 端口 {service_port} 注册失败: {str(e)}")

    # 初始化APScheduler调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: send_heartbeat(nacos_client, service_port), trigger="interval", seconds=10)
    scheduler.start()

def send_heartbeat(nacos_client, service_port):
    try:
        nacos_client.send_heartbeat(
            service_name=NACOS_SERVICE_NAME,
            ip=Local_IP,
            port=service_port,
            group_name=NACOS_GROUP_NAME
        )
        print(f"✅ 端口 {service_port} 心跳发送成功")
    except NacosException as e:
        print(f"❌ 端口 {service_port} 心跳发送失败: {str(e)}")