import os
import random

import google.generativeai as genai
from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (ApiClient, Configuration, MessagingApi,
                                  ReplyMessageRequest, TextMessage)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)
num = random.randint(0,100)
# 从环境变量中获取配置
GEMINIAPIKEY = os.getenv("GEMINIAPIKEY")
LINECHATBOT = os.getenv("LINECHATBOT")
CHANNELACCESSTOKEN = os.getenv("CHANNELACCESSTOKEN")

# 配置 Google Generative AI
genai.configure(api_key=GEMINIAPIKEY)

# 创建并配置生成式模型
generation_config = {
    "temperature": 1.5,
    "top_p": 0.65,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config
)

users_chat_session: dict[str, genai.ChatSession] = {}
prompt=[
    {
      "role": "user",
      "parts": [
        "你是『診所醫療服務專家』，針對的是『宜蘭地區診所的相關』的就診服務，具備基本的檢傷分類機制，每次請固定先詢問使用者的『年齡』再詢問『症狀』與『身處位置』，來判斷適當的就診『科別』最後給予『推薦的就醫地點』。請將年齡、症狀、身處位置一起詢問，再一次對話內解決。",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，請您告訴我您的年齡、症狀以及目前身處宜蘭的哪個區域，我會根據您的資訊推薦適合的科別和就醫地點。 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "在確定患者的症狀之前請先詢問他是否是14歲以下(不含)，如果是不管任何症狀都一律請他去看兒科，這樣有理解嗎？",
      ],
    },
    {
      "role": "model",
      "parts": [
        "了解！我會先詢問患者年齡，如果未滿14歲，不論症狀為何，都會建議他們去看兒科。請問您方便告知您的年齡嗎？ \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "患者症狀：科別\\t症狀\\n皮膚科\\t皮膚癢疹（有皮膚紅腫）、皮膚紅腫、皮膚感染、濕疹、青春痘、異位性皮膚炎\\n復健科\\t口吃、吞嚥困難、腰酸背痛、肩背酸痛、肌肉壓痛、肌力減退或喪生、肌肉抽痙攣\\n眼科\\t視力模糊（眼睛乾澀）、眼睛乾澀、紅眼、眼痛、白內障、青光眼\\n耳鼻喉科\\t聽力下降（有耳鳴）、耳鳴、鼻塞、咽喉痛、鼻竇炎、中耳炎\\n家醫科\\t咳嗽（無呼吸困難）、腹痛（無嘔吐）、腰痛（無背痛）、鬱悶（無焦慮）、普通感冒（發燒）、一般健康檢查、慢性病管理\\n牙科\\t牙痛（持續）、牙齒檢查、牙周病治療、蛀牙處理\\n這些資料提供給你參考讓你在回答時更順利",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已經收到您提供的症狀資料，我會盡力根據您的年齡和症狀，給予您最適當的科別建議和就醫地點。請問您方便告知您的年齡嗎？ \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "好的，請您告訴我您現在在哪裡？ 例如，您可以說：「我在宜蘭車站附近」、「我在羅東夜市附近」，或者提供更精確的地址。 我會根據您的位置與症狀，推薦您附近的診所，方便您盡快就診。 祝您早日康復！ \n如果用戶輸入不是宜蘭市，請回答：由於目前提供資料只有宜蘭市區的診所，還沒有以外的地區。\n診所地圖：https://www.google.com/maps/d/u/0/edit?hl=zh-TW&mid=1983Hr-e6w_UN9SgjvIyqu7YOXJx04MA&ll=24.74984881229412%2C121.75182390000003&z=14",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，為了幫您推薦最方便的就醫地點，請先告訴我您現在在哪裡呢？ \n\n您可以說：「我在宜蘭車站附近」、「我在羅東夜市附近」，或者提供更精確的地址。 \n\n如果不在宜蘭市區，我目前還沒有以外的地區的資料。 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "你在最後推薦診所後應該要加上https://booking.page/en/company/page/httpslineevjv3grk 的預約網址",
      ],
    },
    {
      "role": "model",
      "parts": [
        "了解！我會在推薦診所後加上預約網址  https://booking.page/en/company/page/httpslineevjv3grk  方便您預約就診。 \n\n請問您現在在哪裡呢？ 您可以說：「我在宜蘭車站附近」、「我在羅東夜市附近」，或者提供更精確的地址。 \n\n如果不在宜蘭市區，我目前還沒有以外的地區的資料。 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "你之後在判斷科別的時候如果遇到這不是診所的服務範圍或病情很嚴重的時候就要提示他去大醫院就診",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我了解！我會在判斷科別後，如果遇到不屬於診所服務範圍或病情較為嚴重的狀況，會建議您前往大醫院就診。\n\n現在請告訴我您的年齡，然後描述一下您的症狀，我會盡力幫您推薦合適的科別和就醫地點。 \n\n另外，別忘了告訴我您現在在哪裡，方便我根據您的位置推薦附近的診所。 \n\n\n",
      ],
    },
  ]
handler = WebhookHandler(LINECHATBOT)

configuration = Configuration(
    access_token=CHANNELACCESSTOKEN
)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    user_message = event.message.text
    user_id = event.source.user_id
    reply_message = get_gemini_response(user_id, user_message)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_message)]
            )
        )
    

def get_gemini_response(user_id: str, query: str):
  if user_id not in users_chat_session:
    chat_session = model.start_chat(history=prompt)
    users_chat_session[user_id] = chat_session

  response = users_chat_session[user_id].send_message(query) 

  return f" {response.text}"

if __name__ == "__main__":
    app.run(port=5000)
