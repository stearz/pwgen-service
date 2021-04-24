#/usr/bin/env python3

# imports
import string
import secrets
import random

import flask
from flask import request, jsonify

# init
app = flask.Flask(__name__)
app.config["DEBUG"] = False


# helpers
def _get_int_arg_from_request(arg, the_request):
    if arg in the_request.args:
        return int(request.args[arg])
    else:
        return False


# API route methods
@app.route('/', methods=['GET'])
def home():
    return '''<!DOCTYPE html>
              <html><head><title>pwgenService</title></head><body>
              <h1>PWGen Service</h1>
              <p>Get passwords by sending GET requests to /api/v1/password and include these parameters:</p>
              <p><ul>
                <li>length - the length of the password(s) to genreate</li>
                <li>specials - the number of special characters in the password</li>
                <li>numbers - the number of values the password should include</li>
                <li>count - How many characters should be generated</li>
              </ul></p>
              <p>The generated passwords are returned in a list in JSON format.</p>
              </body></html>'''


@app.route('/api/v1/password', methods=['GET'])
def api_v1_password():
    results = []    

    length = _get_int_arg_from_request("length", request)
    specials = _get_int_arg_from_request("specials", request)
    numbers = _get_int_arg_from_request("numbers", request)
    count = _get_int_arg_from_request("count", request)

    if (length and specials and numbers and count):
        for pw in range(int(count)):
            pw_numbers = ''.join(secrets.choice(string.digits) for i in range(numbers))
            pw_specials = ''.join(secrets.choice('!@#$%&*-_=+;:,./?') for i in range(specials))
            pw_chars = ''.join(secrets.choice(string.ascii_letters) for i in range(length - (numbers + specials)))
            
            pw_list = list(pw_numbers + pw_specials + pw_chars)
            random.shuffle(pw_list)
            password = ''.join(pw_list)
            
            results.append(password)
        return jsonify(results), 200
    else:
        results.append("ERROR: You have not set all required parameters")
        return jsonify(results), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0')
