import base64
import requests
import os
from dotenv import load_dotenv

#加载.env文件
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

if not DEEPSEEK_API_KEY:
    raise ValueError("未读取到DEEPSEEK_API_KEY，请检查 .env文件！")

def encode_image_to_base64(image_path: str) -> str:
    """将本地图片文件编码为 Base64 字符串"""
    with open(image_path, "rb") as image_file:
        base64_data = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_data

def analyze_image_with_deepseek(
    image_path: str,
    prompt: str = "请详细描述这张图片的内容",
    model: str = "deepseek-flash"
) -> str:
    """
    使用 DeepSeek-Flash 多模态API分析图片
    """
    base64_image = encode_image_to_base64(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    print(f"正在分析图片：{image_path} ...")
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        return answer
    else:
        error_msg = f"请求失败：{response.status_code} - {response.text}"
        print(error_msg)
        return error_msg

def extract_text_from_image(image_path: str) -> str:
    """专门用于 OCR：提取图片中的文字"""
    prompt = """
    请提取这张图片中的所有文字内容。
    要求：
    1. 准确还原文字，不要遗漏
    2. 保持原有的段落和格式
    3. 如果有表格，请用表格形式输出
    4. 如果图片中没有文字，请说明
    这是 RUNOOB 教程的 OCR 测试。
    """
    return analyze_image_with_deepseek(image_path, prompt)

def analyze_chart(image_path: str) -> str:
    """专门用于图表分析"""
    prompt = """
    请分析这张图表。
    请回答以下问题：
    1. 这是什么类型的图表（柱状图、折线图、饼图等）？
    2. 图表的标题和坐标轴含义是什么？
    3. 图表传达的主要信息是什么？
    4. 有什么值得注意的趋势或异常？
    这是 RUNOOB 教程的图表分析测试。
    """
    return analyze_image_with_deepseek(image_path, prompt)

# ============================================
# 主程序：演示不同的视觉分析任务
# ============================================
if __name__ == "__main__":
    test_image = "test_images/runoob_test_image.jpg"
    
    if not os.path.exists(test_image):
        print(f"提示：请先准备一张图片，路径：{test_image}")
        print("或者修改代码中的图片路径")
    else:
        # 任务 1：通用图像描述
        print("\n" + "="*50)
        print("任务 1：图像描述")
        print("="*50)
        result1 = analyze_image_with_deepseek(
            test_image,
            "请详细描述这张图片，包括主体、背景、颜色、构图等"
        )
        print(result1)

        # 任务 2：OCR 文字提取
        print("\n" + "="*50)
        print("任务 2：OCR 文字提取")
        print("="*50)
        result2 = extract_text_from_image(test_image)
        print(result2)

        # 任务 3：图表分析（如果图片是图表）
        print("\n" + "="*50)
        print("任务 3：图表分析")
        print("="*50)
        result3 = analyze_chart(test_image)
        print(result3)

        print("\n" + "="*50)
        print("RUNOOB DeepSeek视觉演示完成！")
        print("="*50)