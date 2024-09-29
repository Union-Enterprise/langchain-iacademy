from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv
import re

from initial_setup import setup
from generation import user_doubt, generate_content

#initial setup server
models = setup()

load_dotenv()

app = Flask(__name__)

@app.route('/generate_one', methods=["POST"])
def generate_one():
    data = request.get_json()
    json_string = generate_content(data['input'], models)
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON: resposta vazia ou malformada")
        json_object = {}

    return jsonify(json_object)


@app.route('/generate', methods=["POST"])
def generate():
    json_string = generate_content(models)
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON: resposta vazia ou malformada")
        json_object = {}

    return jsonify(json_string)


@app.route('/doubt', methods=["POST"])
def doubt():
    data = request.get_json()
    try:
        json_string = user_doubt(input_user=data['input'], context=data['context'], previous=data['previous'], models=models)
    except KeyError:
        json_string = user_doubt(input_user=data['input'], context=data['context'], models=models)

    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON: resposta vazia ou malformada")
        json_object = {}

    return json.dumps(json_object, ensure_ascii=False)


if __name__ == '__main__':
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PORT = os.environ.get("PORT")
    app.run(SERVER_NAME, PORT)