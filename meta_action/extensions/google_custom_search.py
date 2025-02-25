"""
搜索引擎
前期配置:
"""
import re
import requests
import json
import aiohttp
import asyncio
from meta_action.config import environ

# 配置你的 API 密钥和自定义搜索引擎 ID
API_KEY = environ.get('GOOGLE_CUSTOM_SEARCH_API_KEY')  # 替换为你的 Google API 密钥
CX = environ.get('GOOGLE_CUSTOM_SEARCH_CX')         # 替换为你的自定义搜索引擎 ID
def google_search(query, api_key=API_KEY, cx=CX, num=10):
    """
    使用 Google 自定义搜索 API 进行搜索
    :param query: 搜索关键词
    :param api_key: Google API 密钥
    :param cx: 自定义搜索引擎 ID
    :param num: 返回结果数量（1-10）
    :return: 搜索结果列表
    """
    if not api_key or not cx: raise ValueError("GOOGLE_CUSTOM_SEARH_API_KEY or GOOGLE_CUSTOM_SEARCH_CX not set in .env")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num  # 每页返回的结果数，最大为 10
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # 检查请求是否成功
    results = response.json()
    
    # 提取并返回搜索结果
    if "items" in results: return results["items"]
    raise ValueError('No result return!')


def display_results(results):
    """返回搜索结果,其中链接被简写为其"""
    if not results:
        raise ValueError('No result return!')
    ret_text=""
    
    for i, item in enumerate(results, 1):
        ret_text+=f"""
{i}. {item['title']}
{item.get('snippet', 'No snippet')}
{simplify_url(item['link'])}
        """
    return ret_text

def simplify_url(url:str):
    match = re.search(r'//([^/]+)', url)
    return match.group(1) if match else ""

def pipe(query):
    """同步调用搜索"""
    try:
        results = google_search(query)
        answer = display_results(results)
        return results, answer, None
    except Exception as e:
        return None, None, e


if __name__=="__main__":
    results, answer, error = pipe('popular search engine API')
    if error:
        raise error
    else:
        print(answer)