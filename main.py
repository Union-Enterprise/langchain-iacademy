from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv
import re

# from initial_setup import setup
from generation import generate_content
from rag import LLMlearning

load_dotenv()

app = Flask(__name__)


llm = LLMlearning()

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
    return


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