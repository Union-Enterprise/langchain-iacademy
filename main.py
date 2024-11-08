from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import re
import json
from werkzeug.utils import secure_filename
from flask_cors import CORS

# from initial_setup import setup
from generation import generate_content, user_doubt
from rag import LLMlearning

load_dotenv()

app = Flask(__name__, static_folder='images', static_url_path='/images')
CORS(app)

llm = LLMlearning()

UPLOAD_FOLDER = './quiz_fonts/'
ALLOWED_EXTENSIONS = {'pdf'}
quiz_filename = ""

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/generate_one', methods=["POST"])
def generate_one():
    data = request.get_json()
    json_string = generate_content(data['input'], llm)
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON: resposta vazia ou malformada")
        json_object = {}

    return jsonify(json_object)

@app.route('/answer_user_questions', methods=["POST"])
def answer_question():
    data = request.get_json()

    if 'content' not in data or 'prompt' not in data or 'chat' not in data:
        return jsonify({"error": "Requisição malformada, faltando parâmetros obrigatórios."}), 400
    
    content = data['content']
    user_prompt = data['prompt']
    chat_history = data['chat']

    try:
        response = user_doubt(user_prompt, content, chat_history, llm)

        return jsonify({"response": response})
    except Exception as e:

        print(f"Erro ao processar a pergunta do usuário: {e}")
        return jsonify({"error": "Ocorreu um erro ao processar sua pergunta. Tente novamente mais tarde."}), 500

@app.route('/generate_content_and_roadmap', methods=["POST"])
def generate():
    data = request.get_json()

    json_string = generate_content(llm, data['id'])
    return jsonify('sucesso')

@app.route('/upload_quiz_pdf', methods=["POST"])
def upload_quiz_pdf():
    global quiz_filename 
    if request.method == 'POST':
        if 'file' not in request.files:
            print("sem arquivo")
            return jsonify({"error": "Nenhum arquivo enviado."}), 400
        file = request.files['file']
        if file.filename == '':
            print('sem arquivo')
            return jsonify({"error": "Nenhum arquivo selecionado."}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            quiz_filename = filename
            return jsonify("upload feito com sucesso")
        else:
            return jsonify({"error": "Tipo de arquivo não permitido."}), 400

@app.route('/generate_quiz', methods=["POST"])
def generate_quiz():
    if quiz_filename:
        quiz = llm.extract_questions_from_pdf(f"{app.config['UPLOAD_FOLDER']}/{quiz_filename}")
        llm.send_questions_to_gemini(quiz)
        return jsonify("Quiz gerado com sucesso")
    else:
        return jsonify("faça o upload do pdf"), 400

if __name__ == '__main__':
    SERVER_NAME = os.environ.get("SERVER_NAME", "localhost")
    PORT = int(os.environ.get("PORT", 5000))  # Certifique-se de converter para int

    app.run(host=SERVER_NAME, port=PORT)
