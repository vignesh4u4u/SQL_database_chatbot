from flask import request, Flask
import mimetypes

app = Flask(__name__)


def is_pdf(filename):
    return mimetypes.guess_type(filename)[0] == 'application/pdf'


def is_image(filename):
    return mimetypes.guess_type(filename)[0].startswith('image/')


def is_text(filename):
    return mimetypes.guess_type(filename)[0] == 'text/plain'


def is_word_document(filename):
    return mimetypes.guess_type(filename)[0] in (
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@app.route(CONTEXT_PATH + "/context-conversational-chatbot/v1/chat", methods=["POST"])
def context_conversational():
    converter_chat = multiple_context_file.ConversationalChatBot()
    try:
        pdf_all_text = ""
        image_all_text = ""
        textfile_all_text = ""
        word_document_all_text = ""

        if "input_prompt" in request.form:
            input_query = request.form["input_prompt"]

            if "context1" in request.files or "context1" in request.form:
                for key in set(request.form.keys()).union(request.files.keys()):
                    if key.startswith("context"):
                        files = request.files.getlist(key)
                        input_context = request.form.get(key, "")

                        for file in files:
                            filename = file.filename
                            if is_pdf(filename):
                                pdf_all_text += converter_chat.process_pdf(file, input_context, key)
                            elif is_image(filename):
                                image_all_text += converter_chat.process_image(file, input_context, key)
                            elif is_text(filename):
                                textfile_all_text += converter_chat.process_text(file, input_context, key)
                            elif is_word_document(filename):
                                word_document_all_text += converter_chat.process_word_document(file, input_context, key)

                # Assuming `documentchatbot` uses the aggregated texts
                return converter_chat.documentchatbot(pdf_all_text, image_all_text, textfile_all_text,
                                                      word_document_all_text)
            else:
                return converter_chat.yorogpt(input_query)
        else:
            return "Error: Missing required parameter 'input_prompt'.", 400

    except Exception as e:
        return {"error": str(e)}, 500
