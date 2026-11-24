import requests
import os
from dotenv import load_dotenv  

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_ASR_API_URL = "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"

if not ZHIPU_API_KEY:
    raise ValueError("未读取到ZHIPU_API_KEY，请检查.env文件！")

def transcribe_audio_with_glm_asr(
    audio_path: str,
    hotwords: list = None,  #智谱用hotwords热词数组，替代原来的prompt
    stream: bool = False
) -> dict:
    """
    参数说明：
        audio_path: 音频文件路径（仅支持 mp3、wav，时长≤30s，文件≤25MB）
        hotwords: 热词列表，提升专业名词识别，示例：["RUNOOB", "大模型", "RAG"]
        stream: 是否开启流式输出，练习默认False
    返回：
        包含转写文本的字典
    """
    #步骤1：检查文件是否存在
    if not os.path.exists(audio_path):
        return {"error": f"文件不存在：{audio_path}"}

    #步骤2：准备请求头
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}"
    }

    #步骤3：准备请求体（multipart/form-data 和 Whisper 格式保持一致）
    files = {
        "file": open(audio_path, "rb")
    }
    data = {
        "model": "glm-asr-2512",  # ✅【改动8】模型名称替换为 glm-asr-2512
        "stream": stream
    }
    if hotwords and isinstance(hotwords, list):
        data["hotwords"] = hotwords

    #步骤4：发送请求
    print(f"正在转写音频：{audio_path} ...")
    response = requests.post(ZHIPU_ASR_API_URL, headers=headers, files=files, data=data)

    # 步骤 5：关闭文件
    files["file"].close()

    # 步骤 6：处理响应
    if response.status_code == 200:
        result = response.json()
        text = result["text"]
        print(f"转写完成，共 {len(text)} 字")
        return {
            "text": text
        }
    else:
        error_msg = f"请求失败：{response.status_code} - {response.text}"
        print(error_msg)
        return {"error": error_msg}

def transcribe_with_timestamps(audio_path: str) -> dict:
    """智谱不支持词级时间戳，仅返回段落级信息"""
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}"
    }
    files = {"file": open(audio_path, "rb")}
    data = {
        "model": "glm-asr-2512",
    }

    response = requests.post(ZHIPU_ASR_API_URL, headers=headers, files=files, data=data)
    files["file"].close()

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return {"error": response.text}

def runoob_meeting_minutes_demo(audio_path: str) -> str:
    """
    实战：生成会议纪要
    步骤 1：用 GLM-ASR 转写录音
    步骤 2：可以调用智谱对话大模型整理成纪要
    """
    # 先转写，hotwords 填入会议里面的专业词汇
    print("第一步：转写会议录音...")
    transcribe_result = transcribe_audio_with_glm_asr(
        audio_path,
        hotwords=["RUNOOB", "技术方案", "RAG", "大模型", "向量库"]
    )

    if "error" in transcribe_result:
        return transcribe_result["error"]

    transcript = transcribe_result["text"]

    # 第二步：你后续可以把 transcript 发给 glm-4-flash 整理会议纪要
    print("第二步：拿到转写文本，后续可调用大模型整理会议纪要...")
    return transcript

# ============================================
# 主程序
# ============================================
if __name__ == "__main__":
    # 准备一个测试音频文件（注意：音频不能超过30秒！）
    test_audio = "voice-sample.wav" 

    if not os.path.exists(test_audio):
        print(f"提示：请准备一个音频文件，命名为 {test_audio}")
        print("⚠️ 重要限制：智谱GLM-ASR-2512音频时长必须 ≤30秒，格式 mp3 / wav")
    else:
        # 任务 1：简单转写，带自定义热词
        print("\n" + "="*50)
        print("任务 1：简单转写（带热词优化）")
        print("="*50)
        result1 = transcribe_audio_with_glm_asr(
            test_audio,
            hotwords=["RUNOOB", "Python", "API"]
        )
        if "text" in result1:
            print("转写结果：")
            print(result1["text"])

        # 任务 2：带段落时间戳的转写
        print("\n" + "="*50)
        print("任务 2：带段落时间戳转写")
        print("="*50)
        result2 = transcribe_with_timestamps(test_audio)
        if "segments" in result2:
            print("段落信息：")
            for seg in result2["segments"][:3]:
                start = round(seg["start"], 2)
                end = round(seg["end"], 2)
                text = seg["text"]
                print(f"[{start}-{end}] {text}")

        print("\n" + "="*50)
        print("RUNOOB GLM-ASR 演示完成！")
        print("="*50)


