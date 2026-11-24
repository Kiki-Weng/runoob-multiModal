from flask import Flask, request, jsonify
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__) #初始化Flask应用

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
client = OpenAI(
    api_key=ZHIPU_API_KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

def process_with_ai(content: str) -> str:
    #先将提示词设置好
    prompt = f"""
    请分析下面的内容，做两件事：
    1. 分类：判断是"问题"、"建议"还是"感谢"
    2. 摘要：用一句话总结核心内容

    内容：
    {content}

    严格只返回JSON，不要额外解释，格式如下：
    {{
        "category": "问题/建议/感谢",
        "summary": "摘要内容"
    }}
    """
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是内容分析助手，输出严格JSON。"},
            {"role": "user", "content": prompt}
            #把系统提示词和用户的内容一起构建成message
        ],
        temperature=0.3
    )
    return resp.choices[0].message.content

#Flask的路由
# @app.route(路径, methods=[请求方式])
@app.route("/webhook", methods=["POST"])
#POST一般用来给服务器发送数据
#在浏览器上直接敲网址进行访问时默认是GET请求，所以这个路由/webhook不能直接在浏览器上访问，直接访问会报错405 Method Not Allowed
#下面紧跟def webhook_handler()函数。
#只要收到发往/webhook的POST请求，就会跑这个函数，读取传过来的content，调用智谱AI，返回结果。
def webhook_handler():
    data = request.get_json()
    print(f"收到 Webhook 数据：{data}")
    content = data.get("content", "")
    if not content:
        return jsonify({"status": "error", "message": "缺少 content 字段"}), 400

    try:
        ai_result = process_with_ai(content)
        print(f"AI 原始返回：{ai_result}")
        parsed_result = json.loads(ai_result)
        category = parsed_result.get("category", "未知")
        summary = parsed_result.get("summary", "")
        return jsonify({
            "status": "success",
            "category": category,
            "summary": summary
        })
    except Exception as e:
        print(f"错误：{e}")
        return jsonify({"status": "error", "message": str(e)}), 500

#Flask的路由
# @app.route(路径, methods=[请求方式])
@app.route("/test", methods=["GET"])
#GET一般用来从服务器拿数据、展示页面，不适合传大量数据。
#GET就是浏览器默认的访问方式，在地址栏输入网址、刷新页面，都是GET请求。
#下面紧跟test_page函数，只要浏览器打开/test，就会返回一段HTML，也就是一个简单的测试表单。
def test_page():
    return """
    <html>
        <body>
            <h1>Webhook 测试页面</h1>
            <textarea id="content" placeholder="输入测试内容" rows="4" cols="60"></textarea>
            <br>
            <button onclick="sendData()">发送</button>
            <div id="result" style="margin-top:20px"></div>
            <script>
            async function sendData(){
                const text = document.getElementById("content").value;
                const res = await fetch("/webhook", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({content: text})
                });
                const data = await res.json();
                document.getElementById("result").innerText = JSON.stringify(data,null,2);
            }
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    print("Webhook 服务启动：http://localhost:5000")
    print("Webhook地址：http://localhost:5000/webhook")
    print("测试表单页：http://localhost:5000/test")
    #启动Flask服务器的命令
    #把上面写好的所有路由（/webhook、/test）跑起来，让电脑监听5000端口
    app.run(port=5000, debug=True)
    #debug=True表示调试模式，代码改了会自动重启服务器，方便开发调试。只能本地练习用，上线时一定要关掉。


