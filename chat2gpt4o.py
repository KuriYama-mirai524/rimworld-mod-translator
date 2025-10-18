import requests
import json
import os
from openai import OpenAI
import time

# 从环境变量获取API密钥
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
GLM_API_KEY = os.getenv('GLM_API_KEY', '')
QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')

def send_chat(message, pormet, use_url2=False):
    url = "https://api.aliyy.cc/v1/chat/completions"
    url2 = 'https://free.zeroai.chat/v1/chat/completions'
    
    # 使用环境变量中的API密钥
    api_key = os.getenv('ALIYY_API_KEY', '')
    if not api_key:
        print("警告：未设置 ALIYY_API_KEY 环境变量")
        return None
        
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
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
    
    if not DEEPSEEK_API_KEY:
        print("警告：未设置 DEEPSEEK_API_KEY 环境变量")
        return None
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com", timeout=10)
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
    
    if not GLM_API_KEY:
        print("警告：未设置 GLM_API_KEY 环境变量")
        return None
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=GLM_API_KEY,
                base_url="https://open.bigmodel.cn/api/paas/v4/",
                timeout=10
            )
            completion = client.chat.completions.create(
                model="glm-4-flash",  
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
    
    if not QWEN_API_KEY:
        print("警告：未设置 QWEN_API_KEY 环境变量")
        return None
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=QWEN_API_KEY,
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

if __name__ == "__main__":
    print(qwen_flash("你好","你好"))