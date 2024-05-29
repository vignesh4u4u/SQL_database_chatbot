from flask import Flask, render_template, request, redirect, url_for
from huggingface_hub import InferenceClient

app = Flask(__name__, template_folder="template")
chat_history = []
client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.1")

def format_prompt(message, history):
    prompt = "<s>"
    for user_prompt, bot_response in history:
        prompt += f"[INST] {user_prompt} [/INST]"
        prompt += f" {bot_response}  "
    prompt += f"[INST] {message} [/INST]"
    return prompt

generate_kwargs = dict(
    temperature=0.7,
    max_new_tokens=3000,
    top_p=0.95,
    repetition_penalty=1.1,
    do_sample=True,
    seed=42,
)

def generate_text(message, history):
    prompt = format_prompt(message, history)
    output = client.text_generation(prompt, **generate_kwargs)
    return output

@app.route('/')
def index():
    return render_template('main-page.html', chat_history=chat_history)

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['message']
    if user_message.strip():
        history = [(msg[0], msg[1]) for msg in chat_history if msg[0] in ['user', 'bot']]
        bot_response = generate_text(user_message, history)
        chat_history.append(('user', user_message))
        chat_history.append(('bot', bot_response))
    return redirect(url_for('index'))

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    chat_history.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5002)