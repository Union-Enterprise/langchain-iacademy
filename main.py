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
    results = []

    contents = [
        "Números e Operações",
        "Números Inteiros",
        "Números Racionais",
        "Números Irracionais",
        "Números Reais",
        "Geometria",
        "Geometria Plana",
        "Círculos: áreas",
        "Círculos: perímetros",
        "Círculos: ângulos",
        "Quadrados: áreas",
        "Quadrados: perímetros",
        "Retângulos: áreas",
        "Retângulos: perímetros",
        "Triângulos: áreas",
        "Triângulos: semelhança",
        "Polígonos: áreas",
        "Polígonos: perímetros",
        "Geometria Espacial",
        "Volume de prismas",
        "Volume de cilindros",
        "Volume de pirâmides",
        "Volume de cones",
        "Volume de esferas",
        "Área de superfícies",
        "Trigonometria",
        "Razões trigonométricas: seno",
        "Razões trigonométricas: cosseno",
        "Razões trigonométricas: tangente",
        "Teorema de Pitágoras",
        "Álgebra",
        "Equações de 1º grau: resolução",
        "Equações de 1º grau: sistemas",
        "Equações de 2º grau: resolução",
        "Equações de 2º grau: Bhaskara",
        "Equações de 2º grau: raízes",
        "Inequações: resolução",
        "Inequações: gráfico",
        "Funções",
        "Função do 1º grau: gráfico",
        "Função do 1º grau: interpretação",
        "Função do 2º grau: gráfico",
        "Função do 2º grau: interpretação",
        "Funções Exponenciais: crescimento",
        "Funções Exponenciais: decrescimento",
        "Funções Logarítmicas: propriedades",
        "Funções Logarítmicas: gráficos",
        "Porcentagem",
        "Cálculo de porcentagens",
        "Aplicações de porcentagem",
        "Média",
        "Mediana",
        "Moda",
        "Estatística",
        "Gráficos: leitura",
        "Gráficos: interpretação",
        "Probabilidade",
        "Cálculo de probabilidades: eventos simples",
        "Eventos independentes",
        "Eventos dependentes",
        "Sequências e Progressões",
        "Progressão Aritmética (PA)",
        "Progressão Geométrica (PG)",
        "Matemática Financeira",
        "Juros simples",
        "Juros compostos",
        "Descontos simples",
        "Descontos compostos",
        "Planejamento financeiro"
    ]


    for content in contents:
        json_string = generate_content(f"gere tudo sobre {content}", models)
        try:
            json_object = json.loads(json_string)
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON: resposta vazia ou malformada")
            json_object = {}
        
        results.append(json_object)

    return jsonify(results)


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