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

genai.configure(api_key=os.environ["AIzaSyC0xHIJ922U7TofueVkuv2QwOp_pjId1Jc"])

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

response = model.generate_content([
  "input: 我想要預約掛號。",
  "output: 好的 請問哪裡不舒服？",
  "input: 我牙齒痛",
  "output: 根據的您的情況建議您掛牙科，請問需要幫您預約嗎？",
  "input: 好",
  "output: (提示用戶輸入)掛號時間、科別、醫師、就醫時段",
  "input: 輸入完成",
  "output: 已預約成功",
  "input: 我想要取消預約",
  "output: 好的(提示用戶輸入)掛號時間、科別、醫師、就醫時段",
  "input: 輸入完成",
  "output: 已取消預約成功",
  "input: 我想要查詢預約",
  "output: 好的(提示用戶輸入)查詢日期、科別、醫師、就醫時段",
  "input: 輸入完成",
  "output: 顯示結果",
  "input: 我想要查詢看診進度",
  "output: 好的(提示用戶輸入)科別、醫師、就醫時段",
  "input: 輸入完成",
  "output: 顯示結果",
  "input: 我想要查看醫師的專長 像是有關牙科的醫生",
  "output: 這方面駱醫師是專業推薦給您，需要幫您預約嗎？",
  "input: 好",
  "output: .....回到預約功能",
  "input: 你是誰",
  "output: 我是一名診所的服務機器人。可以幫您預約掛號、取消預約、查詢預約、查詢看診進度、以及查看醫師專長。請問您今天需要我做些什麼呢？",
  "input: 你是誰",
  "output: ",
])

print(response.text)
