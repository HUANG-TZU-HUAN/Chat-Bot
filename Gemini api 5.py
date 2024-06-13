import os

import requests
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Line Bot 的 Channel Secret 和 Channel Access Token
GEMINIAPIKEY = os.environ["GEMINIAPIKEY"]
LINECHATBOT =  os.environ["LINECHATBOT"]
CHANNELACCESSTOKEN = os.environ["CHANNELACCESSTOKEN"]
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
    url = "https://api.gemini.com/v1/symbols"  # 範例 API endpoint, 需要替換為實際的 Gemini API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # 處理 API 回應資料，這裡只是一個範例
        return f"Gemini API 回應: {data}"
    else:
        return "無法取得 Gemini API 資料"

if __name__ == "__main__":
    app.run(port=5000)
