from flask import Flask, request, jsonify, render_template
import json
from difflib import get_close_matches
from typing import Optional, List, Dict
import google.generativeai as genai
import requests
import base64

# File path as a constant
KNOWLEDGE_BASE_FILE = 'knowledgeBase.json'
KNOWLEDGE_BASE_FILE_2 = 'knowledgeBase2.json'

# Google Generative AI API configuration
GOOGLE_API_KEY = 'AIzaSyDnIKlDiGxBSLhqfnwXyNXdZq_4cjuYhRw'
genai.configure(api_key=GOOGLE_API_KEY)

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
)

app = Flask(__name__)

# Utility functions for both chatbot and article generator
def load_knowledge_base(file_path: str) -> Dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_knowledge_base(data: Dict, file_path: str):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def find_best_match(user_input: str, items: List[str]) -> Optional[str]:
    matches = get_close_matches(user_input, items, n=1, cutoff=0.75)
    return matches[0] if matches else None

# Chatbot specific functions
def save_knowledge_base_chatbot(file_path: str, data: Dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def get_answer_for_question(question: str, knowledge_base: Dict) -> Optional[str]:
    return knowledge_base["questions"].get(question)

# Article generator specific functions
def save_article_to_knowledge_base(topic: str, content: str, file_path: str):
    knowledge_base = load_knowledge_base(file_path)
    new_article = {
        "topic": topic,
        "content": content
    }
    knowledge_base["articles"].append(new_article)
    save_knowledge_base(knowledge_base, file_path)

def get_article_for_topic(topic: str, knowledge_base: Dict) -> Optional[str]:
    for article in knowledge_base["articles"]:
        if article.get("topic") == topic:
            return article.get("content")
    return None

def generate_article_using_api(topic: str) -> str:
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [f"Write an article about {topic}"],
            },
        ]
    )
    response = chat_session.send_message(f"Write an article about {topic}")
    return format_article(response.text)

def format_article(text: str) -> str:
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip().startswith("## "):
            formatted_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.strip().startswith("**") and line.strip().endswith("**"):
            formatted_lines.append(f"<h3>{line[2:-2].strip()}</h3>")
        elif line.strip().startswith("* "):
            formatted_lines.append(f"<li>{line[2:].strip()}</li>")
        elif line.strip():
            formatted_line = line.strip()
            formatted_line = formatted_line.replace('**', '<b>').replace('<b>', '</b>', 1)  # Bold formatting
            formatted_line = formatted_line.replace('*', '<i>').replace('<i>', '</i>', 1)  # Italic formatting
            formatted_lines.append(f"<p>{formatted_line}</p>")
    formatted_article = '\n'.join(formatted_lines)
    return formatted_article

@app.route('/')
def index():
    return render_template('index.html')

# Chatbot routes
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_FILE_2)
    knowledge_base["questions"] = {q["question"]: q["answer"] for q in knowledge_base["questions"]}

    all_questions = list(knowledge_base["questions"].keys())
    best_match = find_best_match(user_input, all_questions)

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        return jsonify({"response": answer})
    else:
        # Generate response using Gemini AI
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        user_input,
                    ],
                },
            ]
        )

        response = chat_session.send_message(user_input)
        generated_response = response.text

        return jsonify({"response": generated_response, "needs_training": False})

@app.route('/train', methods=['POST'])
def train():
    user_input = request.json.get('message')
    new_answer = request.json.get('answer')
    if not user_input or not new_answer:
        return jsonify({"error": "No message or answer provided"}), 400

    knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_FILE_2)
    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
    save_knowledge_base_chatbot(KNOWLEDGE_BASE_FILE_2, {"questions": knowledge_base["questions"]})

    return jsonify({"response": "Thank you! I learned a new response!"})

# Article generator routes
@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.json.get('topic')
    if not user_input:
        return jsonify({"error": "No topic provided"}), 400

    knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_FILE)
    all_topics = [article.get("topic", "") for article in knowledge_base.get("articles", [])]
    best_match = find_best_match(user_input, all_topics)

    if best_match:
        article_content = get_article_for_topic(best_match, knowledge_base)
    else:
        article_content = generate_article_using_api(user_input)
        save_article_to_knowledge_base(user_input, article_content, KNOWLEDGE_BASE_FILE)

    return jsonify({"response": article_content})

@app.route('/get_article', methods=['GET'])
def get_article():
    with open(KNOWLEDGE_BASE_FILE, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/save_edits', methods=['POST'])
def save_edits():
    data = request.get_json()
    with open(KNOWLEDGE_BASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    return '', 204

@app.route('/regenerate_paragraph/<int:paragraph_index>', methods=['GET'])
def regenerate_paragraph(paragraph_index):
    user_input = request.args.get('topic')
    if not user_input:
        return jsonify({"error": "No topic provided"}), 400

    knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_FILE)
    all_topics = [article.get("topic", "") for article in knowledge_base.get("articles", [])]
    best_match = find_best_match(user_input, all_topics)

    if not best_match:
        return jsonify({"error": "No matching topic found"}), 404

    article_content = get_article_for_topic(best_match, knowledge_base)
    paragraphs = article_content.split('</p>')
    if paragraph_index < 0 or paragraph_index >= len(paragraphs):
        return jsonify({"error": "Invalid paragraph index"}), 400

    existing_paragraph = paragraphs[paragraph_index]  # Adjust as needed
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [f"Rewrite the following paragraph: {existing_paragraph}"],
            },
        ]
    )
    response = chat_session.send_message(f"Rewrite the following paragraph: {existing_paragraph}")
    new_paragraph = response.text.strip()

    paragraphs[paragraph_index] = new_paragraph
    updated_content = '</p>'.join(paragraphs)
    for article in knowledge_base["articles"]:
        if article.get("topic") == best_match:
            article["content"] = updated_content

    save_knowledge_base(knowledge_base, KNOWLEDGE_BASE_FILE)
    return jsonify({'new_paragraph': new_paragraph})

@app.route('/generate_image', methods=['POST'])
def generate_image():
    topic = request.json.get('topic')
    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    response = requests.post('https://clipdrop-api.co/text-to-image/v1',
                             files={'prompt': (None, topic, 'text/plain')},
                             headers={'x-api-key': "1c69107871b4697b0aba14efb74d05c4ee3a9a32c88483295eaaac7cd139d645a2317d5be7be24d1906d9c1785ecdd32"})

    if response.ok:
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        image_url = 'data:image/png;base64,' + image_base64
        return jsonify({"image_url": image_url})
    else:
        return jsonify({"error": "Image generation failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
