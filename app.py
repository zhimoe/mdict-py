import logging as log
import os

import pkg_resources
import uvicorn
from fastapi import FastAPI, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

import ai
from ai.dl_modles import download_models
from es import es_indexing
from mdx.mdx_client import BUILDERS, get_definition_mdx, build_dict
from staticfiles import CachedStaticFiles
from file_utils import is_chinese

app = FastAPI()

templates = Jinja2Templates(directory="resources/templates")
app.mount("/static", CachedStaticFiles(directory=pkg_resources.resource_filename(__name__, 'resources/static')),
          name="static")


def qry_word_def_by_dict(text: str, dict_opt: str) -> str:
    """
    query by dict option
    :param text:
    :param dict_opt:
    :return:
    """
    builder = BUILDERS[dict_opt]
    return get_definition_mdx(text, builder)


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/{static_path}")
def static(static_path: str, request: Request):
    folder = pkg_resources.resource_filename(__name__, 'resources/static')
    files = os.listdir(folder)
    if static_path not in files:
        RedirectResponse(url='/static/index.css')
    return RedirectResponse(url=f'/static/{static_path}')


@app.post("/query", response_class=HTMLResponse)
def query(word: str = Form(...)):
    print(f"mdx query for={word}")
    word_def = ''
    if len(word.split(' ')) != 1:
        return ''
    if is_chinese(word):
        word_def += qry_word_def_by_dict(word, 'hycd_3rd')
    else:  # 英文词典
        word_def += qry_word_def_by_dict(word, 'O8C')
        word_def += qry_word_def_by_dict(word, 'LSC4')
    return word_def


def qry_ai_def(text: str, source: str, target: str) -> str:
    return ai.get_prediction(text, source, target)


@app.post("/ai", response_class=HTMLResponse)
def ai_query(word: str = Form(...)):
    text = word
    source, target = "en", "zh"
    if is_chinese(text):
        source, target = target, source
    return qry_ai_def(text, source, target)


if __name__ == '__main__':
    """
    阅读readme和config.ini
    """
    # logger = log.getLogger(__name__)
    # logger.setLevel(log.INFO)
    print(">>>build the mdx databases...")
    build_dict()  # indexing the mdx file content to sqlite3
    print(">>>starting indexing the LSC4 chinese examples to es...")
    es_indexing(BUILDERS['LSC4'])  # es 例句
    print(">>>starting download the ai models...")
    download_models()
    # do not use 127.0.0.1! and request with localhost:8080
    print("mdx server running at http://localhost:8080")
    uvicorn.run("app:app", host="0.0.0.0", port=8080, log_level=log.WARNING)
