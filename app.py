from flask import Flask

import request


app = Flask(__name__)


@app.route('/')
def hello_world():

    transaction = request.get_transaction_by_hash()

    response = request.get_etc20(transaction["result"]["from"])

    return response


if __name__ == '__main__':
    app.run()
