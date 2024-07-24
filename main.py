from flask import Flask, request, jsonify
from timeout_decorator import timeout, TimeoutError
import os
from dotenv import load_dotenv

from user_doubts import user_doubt

load_dotenv()

app = Flask(__name__)

@app.route('/doubt', methods=["POST"])
@timeout(60)
def doubt():
    data = request.get_json()
    try:
        return user_doubt(input=data['input'], context=data['context'], previous=data['previous'])
    except:
        return user_doubt(input=data['input'], context=data['context'])




if __name__ == '__main__':
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PORT = os.environ.get("PORT")
    app.run(SERVER_NAME, PORT)