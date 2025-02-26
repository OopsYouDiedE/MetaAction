import os
from openai import OpenAI,AsyncOpenAI
from meta_action.config import environ
import asyncio
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=environ.get("DASHSCOPE_API_KEY"),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
).chat.completions
def pipe(query):
    completion = None
    try:
        completion = client.create(
            model="deepseek-v3",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
            messages=[
                {'role': 'user', 'content': query}
            ]
        )
        return completion, completion.choices[0].message.content, None
    except Exception as e:
        return completion, None, None
a_client = AsyncOpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=environ.get("DASHSCOPE_API_KEY"),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
).chat.completions
async def a_pipe(query):
    completion = None
    try:
        completion = await a_client.create(
                                             model="deepseek-v3",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
                                             messages=[
                                                 {'role': 'user', 'content': query}
                                             ]
        )
        return completion, completion.choices[0].message.content, None
    except Exception as e:
        return completion, None, e
    
