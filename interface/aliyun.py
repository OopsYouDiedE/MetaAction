import os
import base64
import gradio as gr
import numpy as np
from openai import OpenAI
import io
import wave
import dotenv
dotenv.load_dotenv()
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

def add_wav_header(pcm_data, sample_rate=24000, channels=1, bits_per_sample=16):
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(bits_per_sample // 8)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return buffer.getvalue()

def audio_stream():
    for chunk in completion:  # 假设 completion 已定义
        if chunk.choices:
            if hasattr(chunk.choices[0].delta, "audio"):
                try:
                    audio_string = chunk.choices[0].delta.audio["data"]
                    pcm_bytes = base64.b64decode(audio_string)
                    wav_bytes = add_wav_header(pcm_bytes)
                    yield wav_bytes
                except Exception as e:
                    print(f"解码错误: {e}")

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

    # 处理流式响应
    accumulated_text = ""
    audio_string=''
    first_add_header=False
    for chunk in completion:
        if chunk.choices:
            delta=chunk.choices[0].delta
            if hasattr(delta, "audio"):
                if "data" not in delta.audio:
                  accumulated_text+=delta.audio["transcript"]
                  yield accumulated_text,None
                else:
                    audio_string += delta.audio["data"]
                    
                    yield accumulated_text,None
    wav_bytes = base64.b64decode(audio_string)
    wav_bytes = add_wav_header(wav_bytes)
    yield accumulated_text,wav_bytes


# 创建 Gradio 界面
iface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Textbox(label="输入您的问题"),
        gr.File(label="上传文件（图片、视频、音频）", file_count="multiple")
    ],
    outputs=[
        gr.Text(label="文字回复"),
        gr.Audio(label="音频响应")
    ],
    title="多模态聊天",
    description="输入问题并可选地上传图片、视频或音频文件，与多模态 API 进行交互。"
)

# 启动 Gradio 应用
iface.launch(debug=True)