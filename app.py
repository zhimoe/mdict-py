from bs4 import BeautifulSoup
from flask import Flask, render_template
from flask import request

from lucky import get_random_word
from query import qry_mdx_def

app = Flask(__name__,
            static_url_path='',
            static_folder='resources/static',
            template_folder='resources/templates'
            )


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/query", methods=['POST'])
def query():
    word = request.form.get("word")
    print(f"mdx query for={word}")
    return qry_mdx_def(word)


@app.route("/lucky", methods=['GET'])
def feeling_lucky():
    word = get_random_word()
    print(f"mdx query for={word}")
    return qry_mdx_def(word)


if __name__ == '__main__':
    """
    阅读readme和config.ini
    """
    app.run(debug=True, port=5000)


