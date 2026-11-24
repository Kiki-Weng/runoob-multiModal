import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_IMAGE_API_URL = "https://open.bigmodel.cn/api/paas/v4/images/generations"

if not ZHIPU_API_KEY:
    raise ValueError("未读取到 ZHIPU_API_KEY，请检查 .env 文件！")

def generate_image_with_glm_image(
    prompt: str,
    size: str = "1024x1024",
    save_dir: str = "runoob_generated_images"
) -> dict:
    """返回：dict。包含图片URL和保存路径。"""

    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZHIPU_API_KEY}"
    }
    # 请求体
    payload = {
        "model": "glm-image",
        "prompt": prompt,
        "size": size
    }
    #发送请求
    print(f"正在生成图片，提示词：{prompt[:50]}...")
    response = requests.post(ZHIPU_IMAGE_API_URL, headers=headers, json=payload)
    #处理响应
    if response.status_code == 200:
        result = response.json()
        image_url = result["data"][0]["url"]
        revised_prompt = result["data"][0].get("revised_prompt", prompt)

        print(f"GLM-Image 优化后的提示词：{revised_prompt}")

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 用时间戳生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"runoob_glm_{timestamp}.png"
        filepath = os.path.join(save_dir, filename)

        # 下载图片
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(image_response.content)
            print(f"图片已保存到：{filepath}")

        return {
            "image_url": image_url,
            "filepath": filepath,
            "revised_prompt": revised_prompt
        }
    else:
        error_msg = f"请求失败：{response.status_code} - {response.text}"
        print(error_msg)
        return {"error": error_msg}

def generate_runoob_logo_demo():
    """演示：生成 RUNOOB 风格的 Logo"""
    prompt = """
    为 RUNOOB 教程网站设计一个可爱友好的机器人吉祥物。
    蓝绿色调，现代扁平化设计，白色背景。
    机器人看起来乐于助人且聪明，有大大的友好眼睛。
    简洁干净，适合科技教育品牌。
    """
    return generate_image_with_glm_image(
        prompt=prompt,
        size="1024x1024"
    )

def generate_book_cover_demo():
    """演示：生成书籍封面"""
    prompt = """
    《AI入门教程》书籍封面设计。
    现代极简风格，深蓝紫渐变背景。
    标题文字清晰可读。
    微妙科技元素：浮动几何图形、淡淡的电路纹理。
    专业稳重，适合编程类书籍。
    """
    return generate_image_with_glm_image(
        prompt=prompt,
        size="1024x1792"  # 竖版
    )

def generate_banner_demo():
    """演示：生成横幅广告图"""
    prompt = """
    编程教程网站RUNOOB网页横幅。
    16:9宽幅，青蓝色渐变背景。
    布局干净，预留文字位置。
    抽象科技元素：浮动代码片段、细网格线条。
    专业舒服。
    """
    return generate_image_with_glm_image(
        prompt=prompt,
        size="1792x1024"  # 横版
    )

# ============================================
# 主程序：演示不同的生成任务
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("RUNOOB 智谱 GLM-Image 图片生成演示")
    print("="*60)

    # 任务 1：生成 Logo
    print("\n[任务 1] 生成 Logo ...")
    result1 = generate_runoob_logo_demo()

    # 任务 2：生成书籍封面
    print("\n[任务 2] 生成书籍封面 ...")
    result2 = generate_book_cover_demo()

    # 任务 3：生成横幅
    print("\n[任务 3] 生成横幅 ...")
    result3 = generate_banner_demo()

    print("\n" + "="*60)
    print("所有任务完成！查看 runoob_generated_images 目录")
    print("="*60)







