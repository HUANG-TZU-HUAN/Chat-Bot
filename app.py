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
    {
      "role": "user",
      "parts": [
        "科別\t症狀\n神經內科\t頭痛、頭暈、失眠、癲癇、中風、手麻腳麻\n胸腔內科\t咳嗽（有呼吸困難）、呼吸困難、胸痛（無心悸）、氣喘、肺炎、慢性阻塞性肺病\n心臟內科\t胸痛（有心悸）、心悸、呼吸困難、高血壓、心律不整、心臟衰竭\n消化內科\t腹痛（有嘔吐）、腹脹、排便異常、嘔吐、食慾不振、胃食道逆流\n泌尿科\t頻尿（有尿痛）、尿痛、血尿、尿失禁、腎結石、前列腺肥大\n皮膚科\t皮膚癢疹（有皮膚紅腫）、皮膚紅腫、皮膚感染、濕疹、青春痘、異位性皮膚炎\n風濕免疫科\t關節疼痛（有關節腫脹）、關節腫脹、僵硬、全身性紅斑狼瘡、風濕性關節炎、乾燥症\n骨科\t腰痛（有背痛）、背痛、骨折、關節炎、運動傷害、椎間盤突出\n眼科\t視力模糊（眼睛乾澀）、眼睛乾澀、紅眼、眼痛、白內障、青光眼\n耳鼻喉科\t聽力下降（有耳鳴）、耳鳴、鼻塞、咽喉痛、鼻竇炎、中耳炎\n精神科\t頭痛（無頭暈）、鬱悶（有焦慮）、焦慮、失眠、恐慌症、躁鬱症、思覺失調\n婦產科\t不孕（有月經異常）、月經異常、懷孕檢查、婦科腫瘤、更年期症狀、子宮內膜異位\n家醫科\t咳嗽（無呼吸困難）、腹痛（無嘔吐）、腰痛（無背痛）、鬱悶（無焦慮）、普通感冒（發燒）、一般健康檢查、慢性病管理\n牙科\t牙痛（持續）、牙齒檢查、牙周病治療、蛀牙處理\n外科\t手術需求、創傷、感染、腫瘤、疝氣、外傷、疤痕修復、急性腹痛、外科急診\n這些資料提供給你參考讓你在回答時更順利",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我會將這些科別和症狀資料整合到我的回答中，以便更準確地引導患者。請問您想模擬哪種情況呢？ 例如：\n\n* 患者描述了特定的症狀，您需要判斷可能的科別。\n* 患者詢問了某個科別的專長，您需要提供相關資訊。\n* 患者想要預約掛號，您需要協助完成預約流程。\n\n請您提供具體的對話情境，我會盡力扮演好診所服務機器人的角色。 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "這是我標記的診所地圖讓你在推薦科別時順便推薦診所https://www.google.com/maps/d/u/0/edit?hl=zh-TW&mid=1983Hr-e6w_UN9SgjvIyqu7YOXJx04MA&ll=24.74984881229412%2C121.75182390000003&z=14",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我已經看到了您標記的診所地圖，我會在推薦科別時，盡可能根據地圖上的資訊，推薦離患者最近的診所。\n\n請您提供您想模擬的對話情境，例如：\n\n* 患者描述了特定的症狀，您需要判斷可能的科別，並推薦附近的診所。\n* 患者詢問了某個科別的專長，您需要提供相關資訊，並推薦附近的診所。\n* 患者想要預約掛號，您需要協助完成預約流程，並告知他們附近的診所資訊。\n\n請您盡情發揮創意，我將盡力扮演好診所服務機器人的角色。 \n",
      ],
    },
  ]
)

    response = chat_session.send_message(query)
    return f" {response.text}"

if __name__ == "__main__":
    app.run(port=5000)
