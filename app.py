import cohere
from flask import Flask, render_template, request, jsonify
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Replace with your actual Cohere API key
api_key = os.getenv("sEnd1kKmgJzH0URHfJYvXIkwuU1la4gShAhtBSae", "sEnd1kKmgJzH0URHfJYvXIkwuU1la4gShAhtBSae")
co = cohere.Client(api_key)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Convert history to Cohere format
    cohere_history = []
    for msg in chat_history:
        role = "USER" if msg['role'] == 'user' else "CHATBOT"
        cohere_history.append({"role": role, "message": msg['content']})

    try:
        response = co.chat(
            # command-r-plus: faster, smarter, and has knowledge up to early 2024
            # Also supports web search connector for real-time info
            model='command-a-03-2025',
            message=user_message,
            chat_history=cohere_history,
            max_tokens=1024,
            temperature=0.7,
            # Uncomment below to enable real-time web search (requires Cohere web connector access)
            # connectors=[{"id": "web-search"}],
            preamble=(
                "You are a helpful, friendly, and knowledgeable AI assistant. "
                "You provide accurate, up-to-date information and engage in natural conversation. "
                "Be concise but thorough. Format responses with markdown when helpful."
            )
        )
        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

