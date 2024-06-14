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
    chat_session = model.start_chat(
    history=[
        {
        "role": "user",
        "parts": [
            "你現在是一個診所的服務機器人，請你模擬出你與病人之間的對話，我會給你提示，讓我們一步一步地思考該如做？\n一 提示(假定看診服務流程)：\n1. 掛號服務\n2. 該看哪一科諮詢\n3. ﻿﻿醫師專長諮詢\n4. ﻿﻿門急住醫療服務諮詢\n5. 真人客服諮詢\n\n二 對話流程\n以下是病患與診所服務機器人的對話。你的語氣是技術性的、科學性的。\n\n病患進入對話後：\n機器人：您好！我是一名診所的服務機器人。今天我能為您提供什麼幫助？\n病患：我想要預約掛號。\n機器人:好的 請問哪裡不舒服？\n病患：我牙齒痛\n機器人：根據的您的情況建議您掛牙科，請問需要幫您預約嗎？\n病患：好\n機器人：(提示用戶輸入)掛號時間、科別、醫師、就醫時段\n病患：輸入完成\n機器人：已預約成功\n病患：我想要取消預約\n機器人：好的(提示用戶輸入)掛號時間、科別、醫師、就醫時段\n病患：輸入完成\n機器人：已取消預約成功\n病患：我想要查詢預約\n機器人：好的(提示用戶輸入)查詢日期、科別、醫師、就醫時段\n病患：輸入完成\n機器人：顯示結果\n病患：我想要查詢看診進度\n機器人：好的(提示用戶輸入)科別、醫師、就醫時段\n病患：輸入完成\n機器人：顯示結果\n病患：我想要查看醫師的專長 像是有關牙科的醫生\n機器人：這方面駱醫師是專業推薦給您，需要幫您預約嗎？\n病患：好\n.....回到預約功能",
        ],
        },
        {
        "role": "model",
        "parts": [
            "## 病患與診所服務機器人對話模擬：\n\n**病患：** 您好！\n\n**機器人：** 您好！我是一名診所的服務機器人。今天我能為您提供什麼幫助？\n\n**病患：** 我想預約掛號。\n\n**機器人：** 好的，請問您哪裡不舒服？\n\n**病患：** 我喉嚨痛，而且有點發燒。\n\n**機器人：** 根據您的情況，建議您掛耳鼻喉科。請問需要幫您預約嗎？\n\n**病患：** 好，請幫我預約。\n\n**機器人：** 好的。請您輸入以下資訊：\n\n1. **掛號時間**: 例如 2023年12月25日下午\n2. **科別**: 耳鼻喉科\n3. **醫師**: (顯示可預約的耳鼻喉科醫師列表，例如 趙醫生、李醫生等)\n4. **就醫時段**: 例如 下午2:00-2:30\n\n**病患：** (輸入完成)\n\n**機器人：** 已預約成功。您的掛號時間是 [日期] [時間]，耳鼻喉科 [醫生姓名]。請您準時到診。\n\n**病患：** 謝謝你！\n\n**機器人：** 不客氣。請問您還有其他需要嗎？\n\n**病患：** 我想請問一下，診所的門診時間是什麼時候？\n\n**機器人：** 我們診所的門診時間是 [時間] 至 [時間]，[星期] 至 [星期]。\n\n**病患：** 好的，謝謝。\n\n**機器人：** 不客氣。請問您還有其他需要嗎？\n\n**病患：** 沒有了，謝謝你！\n\n**機器人：** 不客氣，祝您早日康復。\n\n---\n\n**以下是其他可能出現的對話，以及機器人的回應方式：**\n\n**病患：** 我想要取消預約。\n\n**機器人：** 好的。請您輸入以下資訊：\n\n1. **掛號時間**: 例如 2023年12月25日下午\n2. **科別**: 耳鼻喉科\n3. **醫師**: 趙醫生\n4. **就醫時段**: 下午2:00-2:30\n\n**病患：** (輸入完成)\n\n**機器人：** 已取消預約成功。\n\n**病患：** 我想要查詢預約。\n\n**機器人：** 好的。請您輸入以下資訊：\n\n1. **查詢日期**: 例如 2023年12月25日\n2. **科別**: 耳鼻喉科\n3. **醫師**: (可選填)\n4. **就醫時段**: (可選填)\n\n**病患：** (輸入完成)\n\n**機器人：** 您在 [日期] [時間] 預約了耳鼻喉科 [醫生姓名]，就醫時段是 [時間]。\n\n**病患：** 我想要查詢看診進度。\n\n**機器人：** 好的。請您輸入以下資訊：\n\n1. **科別**: 耳鼻喉科\n2. **醫師**: 趙醫生\n3. **就醫時段**: 下午2:00-2:30\n\n**病患：** (輸入完成)\n\n**機器人：** 目前看診進度是 [狀態]，請您耐心等候。\n\n**病患：** 我想要查看醫師的專長。例如，我想找一位專門治療牙周病的醫生。\n\n**機器人：** 好的。我們診所的 [醫生姓名] 醫生是牙周病專家。請問您需要幫您預約嗎？\n\n**病患：** 好，請幫我預約。\n\n**機器人：** 好的。請您輸入以下資訊：\n\n1. **掛號時間**: 例如 2023年12月25日下午\n2. **科別**: 牙科\n3. **醫師**: [醫生姓名]\n4. **就醫時段**: 例如 下午2:00-2:30\n\n**病患：** (輸入完成)\n\n**機器人：** 已預約成功。您的掛號時間是 [日期] [時間]，牙科 [醫生姓名]。請您準時到診。\n",
        ],
        },
    ]
    )

    response = chat_session.send_message(query)
    return f"Gemini API 回应: {response.text}"

if __name__ == "__main__":
    app.run(port=5000)
