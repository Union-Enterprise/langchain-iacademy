from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv

from user_doubts import user_doubt

#initial setup server
from rag import LLMlearning
geometria = LLMlearning('geometria')
models = {'geometria': geometria}


load_dotenv()

app = Flask(__name__)

@app.route('/doubt', methods=["POST"])
def doubt():
    data = request.get_json()
    try:
        json_string = user_doubt(input_user=data['input'], context=data['context'], previous=data['previous'])
    except KeyError:
        json_string = user_doubt(input_user=data['input'], context=data['context'])
    
    json_object = json.loads(json_string)
    return jsonify(json.dumps(json_object, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PORT = os.environ.get("PORT")
    app.run(SERVER_NAME, PORT)