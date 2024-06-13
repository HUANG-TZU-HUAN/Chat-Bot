import os

import google.generativeai as genai
import requests
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)

# Line Bot 的 Channel Secret 和 Channel Access Token
GEMINIAPIKEY = os.environ["GEMINIAPIKEY"]
LINECHATBOT =  os.environ["LINECHATBOT"]
CHANNELACCESSTOKEN = os.environ["CHANNELACCESSTOKEN"]
genai.configure(api_key=GEMINIAPIKEY)
line_bot_api = LineBotApi(CHANNELACCESSTOKEN)
handler = WebhookHandler(LINECHATBOT)


# 處理 Line webhook 請求
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

# 處理收到的訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_message = get_gemini_response(user_message)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

def get_gemini_response(query):
    # 呼叫 Gemini API 取得回應
    response = model.generate_content(query)
    

    return f"Gemini API 回應: {response.text}"
if __name__ == "__main__":
    app.run(port=5000)
