from flask import Flask, request, make_response
from flask_cors import CORS
from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils import load_parser, compile_hn
from hypernetworks.utils import to_graph

app = Flask(__name__)
CORS(app)


@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    hn_str = request.get_json()

    if hn_str:
        hn = Hypernetwork()
        compile_hn(hn, load_parser(), hn_str['str'])

        response = app.response_class(
            response=to_graph(hn, view=False),
            status=200,
            mimetype='text/plain'
        )

    else:
        response = make_response("Not working", 500)

    return response


@app.route('/generate_graphql', methods=['POST'])
def generate_graphql():
    hn_str = request.get_json()

    if hn_str:
        hn = Hypernetwork()
        compile_hn(hn, load_parser(), hn_str['str'])

        response = app.response_class(
            response=to_graph(hn, view=False),
            status=200,
            mimetype='text/plain'
        )

    else:
        response = make_response("Not working", 500)

    return response


if __name__ == '__main__':
    app.run(debug=True)
