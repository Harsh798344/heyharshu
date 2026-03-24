import cohere
from flask import Flask, render_template, request, jsonify
import os
import secrets
import requests

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ── API KEYS ──────────────────────────────────────────────────────
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "sEnd1kKmgJzH0URHfJYvXIkwuU1la4gShAhtBSae")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "d3d886b9120e434aa60d1cfcadeb241a")

co = cohere.Client(COHERE_API_KEY)


# ── ROUTES ────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    chat_history = data.get('history', [])
    language = data.get('language', 'en')  # BCP-47 or simple code

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Map language code → natural language name for preamble
    LANG_NAMES = {
        'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
        'mr': 'Marathi', 'bn': 'Bengali', 'gu': 'Gujarati', 'kn': 'Kannada',
        'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu', 'or': 'Odia',
        'as': 'Assamese', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
        'ar': 'Arabic', 'zh': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean',
        'pt': 'Portuguese', 'ru': 'Russian', 'it': 'Italian',
    }
    lang_name = LANG_NAMES.get(language.split('-')[0], 'English')

    # Convert history to Cohere format
    cohere_history = []
    for msg in chat_history:
        role = "USER" if msg['role'] == 'user' else "CHATBOT"
        cohere_history.append({"role": role, "message": msg['content']})

    preamble = (
        f"You are a helpful, friendly, and knowledgeable AI assistant. "
        f"The user's preferred language is {lang_name}. "
        f"Always respond in {lang_name} unless the user explicitly writes in a different language. "
        f"Be concise but thorough. Format responses with markdown when helpful."
    )

    try:
        response = co.chat(
            model='command-a-03-2025',
            message=user_message,
            chat_history=cohere_history,
            max_tokens=1024,
            temperature=0.7,
            preamble=preamble,
        )
        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/news', methods=['GET'])
def news():
    """Fetch top headlines from NewsAPI with optional category & language filter."""
    category = request.args.get('category', 'general')  # business, entertainment, health, science, sports, technology
    country = request.args.get('country', 'in')  # in, us, gb, etc.
    lang_q = request.args.get('lang', 'en')  # for search queries

    # For non-English content use /everything with language param
    # Top headlines only supports a subset of countries but is easiest
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': NEWS_API_KEY,
        'category': category,
        'country': country,
        'pageSize': 12,
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()

        if data.get('status') != 'ok':
            return jsonify({'error': data.get('message', 'NewsAPI error')}), 500

        articles = []
        for a in data.get('articles', []):
            articles.append({
                'title': a.get('title', ''),
                'description': a.get('description', ''),
                'url': a.get('url', ''),
                'urlToImage': a.get('urlToImage', ''),
                'source': a.get('source', {}).get('name', ''),
                'publishedAt': a.get('publishedAt', ''),
                'content': a.get('content', ''),
            })

        return jsonify({'articles': articles, 'totalResults': data.get('totalResults', 0)})

    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Could not connect to NewsAPI'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/news/search', methods=['GET'])
def news_search():
    """Full-text news search using /everything endpoint."""
    q = request.args.get('q', '')
    language = request.args.get('language', 'en')
    sort_by = request.args.get('sortBy', 'publishedAt')  # relevancy, popularity, publishedAt

    if not q:
        return jsonify({'error': 'Query required'}), 400

    url = "https://newsapi.org/v2/everything"
    params = {
        'apiKey': NEWS_API_KEY,
        'q': q,
        'language': language,
        'sortBy': sort_by,
        'pageSize': 12,
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()

        if data.get('status') != 'ok':
            return jsonify({'error': data.get('message', 'NewsAPI error')}), 500

        articles = []
        for a in data.get('articles', []):
            articles.append({
                'title': a.get('title', ''),
                'description': a.get('description', ''),
                'url': a.get('url', ''),
                'urlToImage': a.get('urlToImage', ''),
                'source': a.get('source', {}).get('name', ''),
                'publishedAt': a.get('publishedAt', ''),
                'content': a.get('content', ''),
            })

        return jsonify({'articles': articles, 'totalResults': data.get('totalResults', 0)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)