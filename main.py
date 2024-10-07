from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import re
import json
from werkzeug.utils import secure_filename
from flask_cors import CORS

# from initial_setup import setup
from generation import generate_content
from rag import LLMlearning

load_dotenv()

app = Flask(__name__)
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


# @app.route('/generate_content', methods=["POST"]) # implementar o get roadmap do banco e gerar conteudo a partir disso
# def generate():
#     json_string = generate_content()
#     try:
#         json_object = json.loads(json_string)
#     except json.JSONDecodeError:
#         print("Erro ao decodificar JSON: resposta vazia ou malformada")
#         json_object = {}

#     return jsonify(json_string)

@app.route('/generate_content_and_roadmap', methods=["POST"])
def generate():
    json_string = generate_content(llm)
    return jsonify('sucesso')


@app.route('/upload_quiz_pdf', methods=["POST"])
def upload_quiz_pdf():
    global quiz_filename 
    if request.method == 'POST':
        if 'file' not in request.files:
            print("sem arquivo")
        file = request.files['file']
        if file.filename == '':
            print('sem arquivo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            quiz_filename = filename
            return jsonify("upload feito com sucesso")

@app.route('/generate_quiz', methods=["POST"])
def generate_quiz():
    if quiz_filename:
        quiz = llm.extract_questions_from_pdf(f"{app.config['UPLOAD_FOLDER']}/{quiz_filename}")
        llm.send_questions_to_gemini(quiz)
    else:
        return jsonify("faça o upload do pdf"), 400


# @app.route('/doubt', methods=["POST"])
# def doubt():
#     data = request.get_json()
#     try:
#         json_string = user_doubt(input_user=data['input'], context=data['context'], previous=data['previous'], models=models)
#     except KeyError:
#         json_string = user_doubt(input_user=data['input'], context=data['context'], models=models)

#     try:
#         json_object = json.loads(json_string)
#     except json.JSONDecodeError:
#         print("Erro ao decodificar JSON: resposta vazia ou malformada")
#         json_object = {}

#     return json.dumps(json_object, ensure_ascii=False)


if __name__ == '__main__':
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PORT = os.environ.get("PORT")
    app.run(SERVER_NAME, PORT)