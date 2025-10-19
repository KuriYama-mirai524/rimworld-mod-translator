import requests
import json
from openai import OpenAI
import time

def send_chat(message, pormet, use_url2=False):
    url = "https://api.aliyy.cc/v1/chat/completions"
    url2 = 'https://free.zeroai.chat/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-RUqxVLekrxJlVOqIcPyapuchbWLHnmXq'
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
            client = OpenAI(api_key="sk-1eab9efcbbf74d9cbadf6bb8eaa509bd", base_url="https://api.deepseek.com", timeout=10)
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
                api_key="9f4a45a9957a86f5ef5267bab5d2330c.uaJ3USMTPN2Quve2",
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
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key="sk-ba91ac98378b41c8af7dd947ce57c811",
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