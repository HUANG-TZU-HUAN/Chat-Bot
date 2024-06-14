import os

import google.generativeai as genai
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 从环境变量中获取配置
GEMINIAPIKEY = os.getenv("GEMINIAPIKEY")
LINECHATBOT = os.getenv("LINECHATBOT")
CHANNELACCESSTOKEN = os.getenv("CHANNELACCESSTOKEN")

# 配置 Google Generative AI
genai.configure(api_key=GEMINIAPIKEY)

# 创建并配置生成式模型
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

line_bot_api = LineBotApi(CHANNELACCESSTOKEN)
handler = WebhookHandler(LINECHATBOT)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_message = get_gemini_response(user_message)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

def get_gemini_response(query):
    # 调用 Gemini API 获取响应
    response = model.generate_content([query])
    return f"Gemini API 回应: {response[0]['text']}"

if __name__ == "__main__":
    app.run(port=5000)
