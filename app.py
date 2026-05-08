from flask import Flask, request, jsonify
import traceback
import os

app = Flask(__name__)

XAI_API_KEY = os.getenv("XAI_API_KEY")  # Берём из переменных Railway

from openai import OpenAI
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

dialogs = {}

@app.route('/', methods=['POST'])
def alice_webhook():
    try:
        req = request.get_json(force=True)
        session_id = req['session']['session_id']
        user_text = req['request'].get('original_utterance', '').strip()

        if not user_text:
            text = "Привет! Я Grok. Чем могу помочь?"
        else:
            if session_id not in dialogs:
                dialogs[session_id] = [{"role": "system", "content": "Ты — Grok от xAI. Отвечай на русском, дружелюбно и с юмором."}]

            dialogs[session_id].append({"role": "user", "content": user_text})

            response = client.chat.completions.create(
                model="grok-4.3",          # Самая актуальная модель
                messages=dialogs[session_id],
                temperature=0.8,
                max_tokens=900
            )
            text = response.choices[0].message.content.strip()

            dialogs[session_id].append({"role": "assistant", "content": text})

        return jsonify({
            "version": "1.0",
            "session": req['session'],
            "response": {"text": text, "end_session": False}
        })

    except Exception as e:
        print("=== ОШИБКА ===")
        print(str(e))
        print(traceback.format_exc())
        return jsonify({
            "version": "1.0",
            "session": req.get('session', {}),
            "response": {"text": "Извини, проблемы с соединением. Попробуй ещё раз.", "end_session": False}
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)