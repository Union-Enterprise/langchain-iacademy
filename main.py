from flask import Flask, request
import json
import os
from dotenv import load_dotenv

from initial_setup import setup
from user_doubts import user_doubt

#initial setup server
models = setup()

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
    return json.dumps(json_object, ensure_ascii=False)


if __name__ == '__main__':
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PORT = os.environ.get("PORT")
    app.run(SERVER_NAME, PORT)