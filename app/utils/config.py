import os
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import socket

# Load environment variables
load_dotenv()
def get_local_ip():
    try:
        if os.name == "nt":  # Windows
            return socket.gethostbyname(socket.gethostname())
        else:  # Linux 或 Mac
            output = os.popen("hostname -I").read().strip()
            return output.split()[0] if output else "127.0.0.1"
    except Exception as e:
        print(f"获取本机 IP 失败: {e}")
        return os.getenv("LOCAL_IP", "")

class Settings(BaseModel):
    # OpenAI API configuration
    openai_api_key: str = os.getenv("API_KEY", "")
    openai_default_model: str = os.getenv("MODEL_ID", "deepseek-ai/DeepSeek-R1/lcqfpp5osj")
    openai_api_base: str = os.getenv("BASE_URL", "")


    # Nacos configuration
    nacos_server_address: str = os.getenv("NACOS_SERVER_ADDRESS", "")
    nacos_namespace: str = os.getenv("NACOS_NAMESPACE", "")
    nacos_service_name: str = os.getenv("NACOS_SERVICE_NAME", "")
    nacos_group_name: str = os.getenv("NACOS_GROUP_NAME", "")
    nacos_port: int = int(os.getenv("NACOS_PORT", "8848"))

    
    # Service configuration
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    log_level: str = os.getenv("LOG_LEVEL", "info")

    local_ip: str = get_local_ip()




# Create settings instance
settings = Settings()

# Validate required configuration
if not settings.openai_api_key:
    raise ValueError("API_KEY must be set in .env file or environment variables") 