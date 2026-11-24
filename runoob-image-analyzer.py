import base64
import requests
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class RunoobImageAnalyzer:
    """RUNOOB图片分析器，一个封装好的多模态工具类"""
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn/api/paas/v4"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def _encode_image(self, image_path: str) -> str:
        """将图片编码为 Base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _call_vision_api(
        self,
        image_path: str,
        prompt: str,
        model: str = "glm-4v",  #智谱glm-4v
        max_tokens: int = 2000
    ) -> Optional[str]:
        """内部方法：调用视觉API"""
        base64_image = self._encode_image(image_path)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }

        url = f"{self.base_url}/chat/completions"
        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API 错误：{response.status_code} - {response.text}")
            return None

    def describe(self, image_path: str) -> Optional[str]:
        """详细描述图片内容"""
        prompt = """
        请详细描述这张图片，包括：
        1. 主体内容（有什么人/物）
        2. 背景环境
        3. 颜色和光线
        4. 整体氛围
        用中文回答，结构清晰。
        """
        return self._call_vision_api(image_path, prompt)

    def extract_text(self, image_path: str) -> Optional[str]:
        """提取图片中的所有文字（OCR）"""
        prompt = """
        请提取这张图片中的所有文字内容。
        要求：
        1. 准确还原，不要遗漏
        2. 保持原有的段落结构
        3. 如果是表格，请用 Markdown 表格格式输出
        4. 如果没有文字，请明确说明"图片中没有可识别的文字"
        """
        return self._call_vision_api(image_path, prompt)

    def analyze_ui(self, image_path: str) -> Optional[str]:
        """分析 UI 设计稿（截图）"""
        prompt = """
        请分析这张 UI 设计稿：
        1. 这是什么类型的界面（APP、网页、小程序等）？
        2. 界面的主要功能模块有哪些？
        3. 设计风格如何（配色、布局、字体）？
        4. 有什么可改进的地方？
        用中文回答，分点列出。
        """
        return self._call_vision_api(image_path, prompt)

    def analyze_product(self, image_path: str) -> Optional[str]:
        """分析商品图片，生成电商文案"""
        prompt = """
        请分析这张商品图片，生成一段电商文案。
        文案应包括：
        1. 商品名称和类型
        2. 外观特点（颜色、材质、设计）
        3. 一个吸引人的简短推荐语（30-50字）
        用中文回答，语气友好积极。
        """
        return self._call_vision_api(image_path, prompt)

    def classify(self, image_path: str, categories: list = None) -> Optional[str]:
        """对图片进行分类"""
        if categories is None:
            categories = [
                "人物照片", "风景照片", "美食照片", "产品照片",
                "设计稿/截图", "文档/表格", "图表/数据可视化", "其他"
            ]
        cat_list = "、".join(categories)
        prompt = f"""
        请判断这张图片属于哪个类别。
        可选类别：{cat_list}
        请只返回最匹配的一个类别名称，不要其他文字。
        """
        return self._call_vision_api(image_path, prompt)

    def full_analysis(self, image_path: str, output_dir: str = "runoob_analysis") -> Dict[str, Any]:
        """
        完整分析：生成一份详细的分析报告
        返回一个字典，包含所有分析结果
        """
        print(f"开始分析图片：{image_path}")

        # 先分类
        print("[1/5] 分类中...")
        category = self.classify(image_path) or "未知"

        # 描述
        print("[2/5] 描述中...")
        description = self.describe(image_path) or ""

        # 提取文字
        print("[3/5] OCR 中...")
        text = self.extract_text(image_path) or ""

        # 根据类别做专项分析
        print("[4/5] 专项分析中...")
        special_analysis = ""
        if "设计" in category or "截图" in category:
            special_analysis = self.analyze_ui(image_path) or ""
        elif "产品" in category or "商品" in category:
            special_analysis = self.analyze_product(image_path) or ""

        # 保存报告
        print("[5/5] 生成报告中...")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "image_file": os.path.basename(image_path),
            "analysis_time": datetime.now().isoformat(),
            "category": category,
            "description": description,
            "extracted_text": text,
            "special_analysis": special_analysis
        }

        # 保存 JSON
        json_path = os.path.join(output_dir, f"report_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 保存可读文本
        txt_path = os.path.join(output_dir, f"report_{timestamp}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("RUNOOB 图片分析报告\n")
            f.write("="*60 + "\n\n")
            f.write(f"图片：{report['image_file']}\n")
            f.write(f"时间：{report['analysis_time']}\n")
            f.write(f"分类：{report['category']}\n\n")
            f.write("-"*60 + "\n")
            f.write("图片描述：\n")
            f.write("-"*60 + "\n")
            f.write(report["description"] + "\n\n")
            f.write("-"*60 + "\n")
            f.write("提取文字：\n")
            f.write("-"*60 + "\n")
            f.write(report["extracted_text"] + "\n\n")
            if report["special_analysis"]:
                f.write("-"*60 + "\n")
                f.write("专项分析：\n")
                f.write("-"*60 + "\n")
                f.write(report["special_analysis"] + "\n")

        print(f"分析完成！报告已保存到：{output_dir}")
        return report

def main():
    #【修改】加载同目录下 .env 文件里面的密钥
    load_dotenv()
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 错误：请检查当前目录的 .env 文件，配置 ZHIPU_API_KEY")
        return

    # 创建分析器
    analyzer = RunoobImageAnalyzer(api_key)

    # 要分析的图片路径
    image_path = "runoob_test_image.jpg"

    if not os.path.exists(image_path):
        print(f"❌ 请先准备图片：{image_path}，放到当前文件夹")
        return

    # 方式 1：单独使用某个功能
    print("\n方式 1：单独使用 OCR 功能")
    print("-"*40)
    text = analyzer.extract_text(image_path)
    if text:
        print("提取的文字：")
        print(text)

    # 方式 2：完整分析
    print("\n方式 2：完整分析")
    print("-"*40)
    report = analyzer.full_analysis(image_path)
    print(f"分类结果：{report['category']}")
    print(f"报告已保存")

if __name__ == "__main__":
    main()




