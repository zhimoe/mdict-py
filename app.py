import logging as log
import os

import pkg_resources
import uvicorn
from fastapi import FastAPI, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from query import qry_mdx_def, qry_ai_def
from staticfiles import CachedStaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="resources/templates")
app.mount("/static", CachedStaticFiles(directory=pkg_resources.resource_filename(__name__, 'resources/static')),
          name="static")


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
    return qry_mdx_def(word)


@app.post("/ai", response_class=HTMLResponse)
def ai_query(word: str = Form(...)):
    return qry_ai_def(word)


if __name__ == '__main__':
    """
    阅读readme和config.ini
    """
    # logger = log.getLogger(__name__)
    # logger.setLevel(log.INFO)
    # do not use 127.0.0.1! and request with localhost:8080
    print("mdx server running at http://localhost:8080")
    uvicorn.run("app:app", host="0.0.0.0", port=8080, log_level=log.WARNING)
