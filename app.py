from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from openai import OpenAI  # ✅ 新版 OpenAI SDK

app = Flask(__name__)

# 讀取環境變數
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ 建立 GPT 客戶端

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # ✅ 呼叫 GPT 模型（新版 SDK 寫法）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 或 gpt-4，看你有沒有授權
            messages=[
                {"role": "system", "content": "你是一位親切、有趣的 LINE 機器人"},
                {"role": "user", "content": user_message}
            ]
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"錯誤訊息：{str(e)}"  # ✅ 可移除：除錯用

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
