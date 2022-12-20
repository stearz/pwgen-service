#!/usr/bin/env python3

# imports
import string
import secrets
import random

import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracing
from flask import Flask, request, jsonify
from waitress import serve
from os import getenv
JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')

# init
app = Flask(__name__)
app.config["DEBUG"] = False

log_level = logging.DEBUG
logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

config = Config(config={'sampler': {'type': 'const', 'param': 1},
                        'logging': True,
                        'local_agent': {'reporting_host': JAEGER_HOST}},
                service_name="pwgenService")
jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer)


def _get_int_arg_from_request(arg, the_request):
    if arg in the_request.args:
        return int(request.args[arg])
    else:
        return False


@app.route('/', methods=['GET'])
@tracing.trace()   # Indicate that endpoint should be traced
def home():
    # Extract the span information for request object.
    with jaeger_tracer.start_active_span(
            'rendering homepage') as scope:

        status_code = 200
        data = '''<!DOCTYPE html>
        <html><head><title>pwgenService</title></head><body>
        <h1>pwgenService</h1>
        <p>Get passwords by sending GET requests to /api/v1/password and
           include these parameters:</p>
        <p><ul>
          <li>length - the length of the password(s) to genreate</li>
          <li>specials - the number of special characters in the password</li>
          <li>numbers - the number of values the password should include</li>
          <li>count - How many characters should be generated</li>
        </ul></p>
        <p>Example:
        <a href="/api/v1/password?length=14&specials=2&numbers=2&count=5">
            /api/v1/password?length=14&specials=2&numbers=2&count=5
        </a></p>
        <p>The generated passwords are returned as a list in JSON format.</p>
        </body></html>'''

        scope.span.log_kv({'event': 'sending response',
                           'result': status_code})
    return data, status_code


@app.route('/api/v1/password', methods=['GET'])
@tracing.trace()   # Indicate that endpoint should be traced
def api_v1_password():
    results = []

    length = _get_int_arg_from_request("length", request)
    specials = _get_int_arg_from_request("specials", request)
    numbers = _get_int_arg_from_request("numbers", request)
    count = _get_int_arg_from_request("count", request)

    # Extract the span information for request object.
    with jaeger_tracer.start_active_span(
            'generating password list from inputs') as scope:

        if (length and specials and numbers and count):
            for pw in range(int(count)):
                pw_numbers = ''.join(secrets.choice(string.digits)
                                     for i in range(numbers))
                pw_specials = ''.join(secrets.choice('!@#$%&*-_=+;:,./?')
                                      for i in range(specials))
                pw_chars = ''.join(secrets.choice(string.ascii_letters)
                                   for i in range(length -
                                                  (numbers + specials)))

                pw_list = list(pw_numbers + pw_specials + pw_chars)
                random.shuffle(pw_list)
                pw = ''.join(pw_list)

                scope.span.log_kv({'event': 'password generated'})
                results.append(pw)
            status_code = 200
        else:
            results.append("ERROR: You have not set all required parameters")
            status_code = 400

        scope.span.log_kv({'event': 'sending response',
                           'result': status_code})
    return jsonify(results), status_code


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)
