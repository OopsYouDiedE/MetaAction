import asyncio
from openai import AsyncOpenAI


class BaseOpenAILLM:
    total_cost = 0  # 类变量，用于统计所有实例的总花费

    def __init__(
        self,
        api_key,
        base_url,
        model_name,
        system_prompt=None,
        input_price_per_token=0.000002,
        output_price_per_token=0.000002,
        **kwargs
    ):
        """
        初始化 LLM 类，设置 API 密钥、基础 URL 和模型参数。

        参数:
            api_key (str): OpenAI API 密钥
            base_url (str): OpenAI API 基础 URL
            model_name (str): 使用的模型名称，例如 "gpt-3.5-turbo"
            input_price_per_token (float): 每输入 token 的价格（美元），默认为 0.000002
            output_price_per_token (float): 每输出 token 的价格（美元），默认为 0.000002
            **kwargs: 其他可选参数，例如 temperature、max_tokens 等
        """
        self.client = AsyncOpenAI(
            api_key=api_key, base_url=base_url)  # 创建 AsyncOpenAI 客户端实例
        self.model_name = model_name  # 设置使用的模型名称
        self.system_prompt = system_prompt
        self.input_price_per_token = input_price_per_token  # 设置每输入 token 的价格
        self.output_price_per_token = output_price_per_token  # 设置每输出 token 的价格
        self.kwargs = kwargs

    async def async_run(self, message):
        """
        异步运行函数，接收消息并流式输出模型响应，同时统计 token 使用量和总花费。

        参数:
            message (str): 用户输入的消息

        返回:
            异步生成器，逐个 yield 模型返回的 token
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": message})
        stream = await self.client.chat.completions.create(  # 异步创建聊天完成请求
            model=self.model_name,  # 使用指定的模型
            messages=[{"role": "user", "content": message}],  # 用户输入的消息
            stream=True,  # 启用流式输出
            stream_options={"include_usage": True},
            **self.kwargs  # 其他可选参数
        )
        output_text = ""  # 初始化输出文本
        async for chunk in stream:  # 异步遍历流式输出的数据块
            if chunk.choices:  # 如果有返回的选项
                token = chunk.choices[0].delta.content  # 获取当前 token
                output_text += token  # 将 token 添加到输出文本
                yield token
            print(chunk)
            if hasattr(chunk, 'usage'):  # 如果数据块中包含使用量信息
                if not chunk.usage:
                    continue
                self.total_cost += (  # 更新总花费
                    self.input_price_per_token * chunk.usage.prompt_tokens  # 输入 token 的花费
                    + self.output_price_per_token * chunk.usage.completion_tokens  # 输出 token 的花费
                )


class AlibabaDeepseekR1LLM(BaseOpenAILLM):
    total_cost = 0  # 类变量，用于统计所有实例的总花费

    def __init__(
        self,
        api_key,
        system_prompt=None,
        input_price_per_token=0.004/1000,
        output_price_per_token=0.016/1000,
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name='deepseek-r1',
            system_prompt=system_prompt,
            input_price_per_token=input_price_per_token,
            output_price_per_token=output_price_per_token,
            **kwargs
        )
        """
        初始化 LLM 类，设置 API 密钥、基础 URL 和模型参数。

        参数:
            api_key (str): OpenAI API 密钥
            base_url (str): OpenAI API 基础 URL
            model_name (str): 使用的模型名称，例如 "gpt-3.5-turbo"
            input_price_per_token (float): 每输入 token 的价格（美元），默认为 0.000002
            output_price_per_token (float): 每输出 token 的价格（美元），默认为 0.000002
            **kwargs: 其他可选参数，例如 temperature、max_tokens 等
        """

    async def async_run(self, message):
        """
        异步运行函数，接收消息并流式输出模型响应，同时统计 token 使用量和总花费。

        参数:
            message (str): 用户输入的消息

        返回:
            异步生成器，逐个 yield 模型返回的 token
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": message})
        stream = await self.client.chat.completions.create(  # 异步创建聊天完成请求
            model=self.model_name,  # 使用指定的模型
            messages=[{"role": "user", "content": message}],  # 用户输入的消息
            stream=True,  # 启用流式输出
            stream_options={"include_usage": True},
            **self.kwargs  # 其他可选参数
        )
        output_text = ""  # 初始化输出文本
        reasoning_content = ""
        async for chunk in stream:  # 异步遍历流式输出的数据块
            if not chunk.choices:
                self.total_cost += (  # 更新总花费
                    self.input_price_per_token * chunk.usage.prompt_tokens  # 输入 token 的花费
                    + self.output_price_per_token * chunk.usage.completion_tokens  # 输出 token 的花费
                )
                continue
            else:  # 如果有返回的选项
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                    print(delta.reasoning_content, end='', flush=True)
                    reasoning_content += delta.reasoning_content
                else:
                    token = chunk.choices[0].delta.content  # 获取当前 token
                    output_text += token  # 将 token 添加到输出文本
                    yield token


class AlibabaDeepseekV3LLM(BaseOpenAILLM):
    total_cost = 0  # 类变量，用于统计所有实例的总花费

    def __init__(
        self,
        api_key,
        system_prompt=None,
        ** kwargs
    ):
        super().__init__(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name='deepseek-v3',
            system_prompt=system_prompt,
            input_price_per_token=0.002/1000,
            output_price_per_token=0.008/1000,
            **kwargs
        )
