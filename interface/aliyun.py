import os
import base64
import gradio as gr
import numpy as np
from openai import OpenAI

# 设置 OpenAI 客户端以使用 DashScope API
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 文件扩展名到 MIME 类型的映射
mime_types = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'ogg': 'audio/ogg',
}

def process_input(text, files):
    """
    处理用户输入，调用 API 并处理流式响应。
    
    参数：
        text (str): 用户输入的文本。
        files (List[File]): 用户上传的文件列表。
    
    返回：
        流式更新文本和音频输出。
    """
    # 构造消息内容
    content = [{"type": "text", "text": text}]
    for file in files or []:
        # 获取文件扩展名
        ext = os.path.splitext(file.name)[1][1:].lower()
        mime_type = mime_types.get(ext, 'application/octet-stream')
        # 读取文件并编码为 base64
        with open(file.name, "rb") as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_data}"
        # 根据文件类型添加到内容中
        if mime_type.startswith('image/'):
            content.append({
                "type": "image_url",
                "image_url": {"url": data_url}
            })
        elif mime_type.startswith('video/'):
            content.append({
                "type": "video_url",
                "video_url": {"url": data_url}
            })
        elif mime_type.startswith('audio/'):
            content.append({
                "type": "input_audio",
                "input_audio": {"data": data_url, "format": ext}
            })
        else:
            # 跳过未知类型
            pass
    print('输入',[x['type']for x in content])
    # 调用 API，启用流式处理
    completion = client.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
            {"role": "user", "content": content}
        ],
        stream=True,
        modalities=["text", "audio"],
        audio={"voice": "Cherry", "format": "wav"}
    )
    import tempfile
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    
    # 处理流式响应
    accumulated_text = ""
    audio_string=''
    for chunk in completion:
        if chunk.choices:
            delta=chunk.choices[0].delta
            if hasattr(delta, "audio"):
                if "data" in delta.audio:
                    audio_string = delta.audio["data"]
                    wav_bytes = base64.b64decode(audio_string)
                    yield wav_bytes


# 创建 Gradio 界面
iface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Textbox(label="输入您的问题"),
        gr.File(label="上传文件（图片、视频、音频）", file_count="multiple")
    ],
    outputs=[
        gr.Audio(label="音频响应",streaming=True)
    ],
    title="多模态聊天",
    description="输入问题并可选地上传图片、视频或音频文件，与多模态 API 进行交互。"
)

# 启动 Gradio 应用
iface.launch()