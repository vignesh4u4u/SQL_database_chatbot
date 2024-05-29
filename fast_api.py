from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from huggingface_hub import InferenceClient

app = FastAPI()
templates = Jinja2Templates(directory="template")
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

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('main-page.html', {'request': request, 'chat_history': chat_history})

@app.post('/send_message')
async def send_message(message: str = Form(...)):
    user_message = message.strip()
    if user_message:
        history = [(msg[0], msg[1]) for msg in chat_history if msg[0] in ['user', 'bot']]
        bot_response = generate_text(user_message, history)
        chat_history.append(('user', user_message))
        chat_history.append(('bot', bot_response))
    return RedirectResponse(url='/', status_code=303)

@app.post('/clear_chat')
async def clear_chat():
    chat_history.clear()
    return RedirectResponse(url='/', status_code=303)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002, reload=True)
