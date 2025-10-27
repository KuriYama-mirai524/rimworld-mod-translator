import requests
import json
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def send_chat(message, pormet, use_url2=False):
    url = "https://api.aliyy.cc/v1/chat/completions"
    url2 = 'https://free.zeroai.chat/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.getenv('ALIYY_API_KEY')}"
    }
    data = {
        "model": "gpt-4o-mini",
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": pormet
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.7, 
        "presence_penalty": 1, 
        "frequency_penalty": 1.1, 
        "top_p": 1, 
        "max_tokens": 400
    }

    max_retries = 3
    retry_delay = 1
    url_to_use = url2 if use_url2 else url
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url_to_use, headers=headers, data=json.dumps(data), timeout=10)
            if response.status_code == 200:
                result = response.json()
                result = result['choices'][0]['message']
                return result['content']
            else:
                print(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
            time.sleep(retry_delay)
            retry_delay *= 2

def deepseek(message, pormet):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com", timeout=10)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": pormet},
                    {"role": "user", "content": message},
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
            time.sleep(retry_delay)
            retry_delay *= 2

def glm(message, pormet):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=os.getenv('GLM_API_KEY'),
                base_url="https://open.bigmodel.cn/api/paas/v4/",
                timeout=10
            )
            completion = client.chat.completions.create(
                model="glm-4-Air",  
                messages=[    
                    {"role": "system", "content": pormet},    
                    {"role": "user", "content": message} 
                ],
                top_p=0.7,
                temperature=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
            time.sleep(retry_delay)
            retry_delay *= 2

def qwen_flash(message, pormet):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=os.getenv('QWEN_API_KEY'),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                timeout=10
            )
            completion = client.chat.completions.create(
                model="qwen-flash",
                messages=[
                    {"role": "system", "content": pormet},
                    {"role": "user", "content": message}
                ],
                top_p=0.7,
                temperature=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
            time.sleep(retry_delay)
            retry_delay *= 2

def call_model(model_name: str, message: str, pormet: str, api_key: str = "", base_url: str = ""):
    """
    通用模型调用函数
    Args:
        model_name: 模型名称 (glm, deepseek, qwen, gpt)
        message: 用户消息
        pormet: 系统提示词
        api_key: API密钥
        base_url: API基础URL
    """
    # 设置环境变量以便现有函数使用
    if api_key:
        env_key = f"{model_name.upper()}_API_KEY"
        os.environ[env_key] = api_key
    
    # 根据模型名称调用相应的函数
    if model_name.lower() == "glm":
        return glm(message, pormet)
    elif model_name.lower() == "deepseek":
        return deepseek(message, pormet)
    elif model_name.lower() == "qwen":
        return qwen_flash(message, pormet)
    elif model_name.lower() == "gpt":
        return send_chat(message, pormet)
    else:
        # 默认使用GLM
        return glm(message, pormet)

if __name__ == "__main__":
    print(qwen_flash("你好","你好"))