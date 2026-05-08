from flask import Flask, request, jsonify
import traceback
import sys

app = Flask(__name__)

XAI_API_KEY = "xai-Iyo5yTY78S2r1He9QF2nxFWCCW7Pfj9xaHt4a5A1G7Iz4gtA1jrQG7g3XYYVvjUELF4Ds9crzatIeEqc"

from openai import OpenAI
client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

dialogs = {}

@app.route('/', methods=['POST', 'GET'])
def alice_webhook():
    print("=== НОВЫЙ ЗАПРОС ОТ ЯНДЕКСА ===", file=sys.stderr)
    print(request.get_json(force=True), file=sys.stderr)
    print("=================================", file=sys.stderr)

    try:
        req = request.get_json(force=True)
        session_id = req['session']['session_id']
        user_text = req['request'].get('original_utterance', '').strip()

        if not user_text:
            text = "Привет! Это Grok. Чем могу помочь?"
        else:
            if session_id not in dialogs:
                dialogs[session_id] = [{"role": "system", "content": "Ты — Grok. Отвечай на русском, с юмором."}]
            
            dialogs[session_id].append({"role": "user", "content": user_text})

            response = client.chat.completions.create(
                model="grok-4.3",   # актуальная модель
                messages=dialogs[session_id],
                temperature=0.8,
                max_tokens=800
            )
            text = response.choices[0].message.content.strip()

            dialogs[session_id].append({"role": "assistant", "content": text})

        return jsonify({
            "version": "1.0",
            "session": req['session'],
            "response": {"text": text, "end_session": False}
        })

    except Exception as e:
        print("=== ОШИБКА ===", file=sys.stderr)
        print(str(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({
            "version": "1.0",
            "session": req.get('session', {}),
            "response": {"text": "Ошибка соединения. Попробуй ещё раз.", "end_session": False}
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)