import logging

from flask import Flask, render_template, request

from lucky import get_random_word
from query import qry_mdx_def

app = Flask(__name__,
            static_url_path='',
            static_folder='resources/static',
            template_folder='../resources/templates'
            )

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
app.logger.propagate = False
log.propagate = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/query", methods=['POST'])
def query():
    word = request.form.get("word")
    log.info(f">>>mdx query for={word}")
    return qry_mdx_def(word)


@app.route("/lucky", methods=['GET'])
def feeling_lucky():
    word = get_random_word()
    log.info(f"mdx query for={word}")
    return qry_mdx_def(word)


if __name__ == '__main__':
    """
    阅读readme和config.ini
    """
    log.info(">>> flask app running...")
    app.run(debug=False, port=5000)
