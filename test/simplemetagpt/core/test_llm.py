import pytest
from unittest.mock import AsyncMock, patch
from simplemetagpt.core.llm import BaseOpenAILLM, AlibabaDeepseekR1LLM
from dotenv import load_dotenv
import os

load_dotenv()
# 从环境变量中读取 api_key 和 base_url


@pytest.fixture
def llm_instance():
    return BaseOpenAILLM(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-turbo",
        input_price_per_token=0.0003/1000,
        output_price_per_token=0.0006/1000
    )


@pytest.fixture
def alibaba_llm_instance():
    return AlibabaDeepseekR1LLM(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    )


@pytest.mark.asyncio
async def test_async_run(llm_instance):
    message = "Hello, world!"
    out = ""
    client = llm_instance

    async for token in client.async_run("Only return Hello, don't return anything else."):
        out += token
    assert out != ""
    assert client.total_cost != 0


@pytest.mark.asyncio
async def test_alibaba_async_run(alibaba_llm_instance):
    message = "9.8和9.11哪个大"
    out = ""
    client = alibaba_llm_instance

    async for token in client.async_run(message):
        out += token
    assert out != ""
    assert client.total_cost != 0
