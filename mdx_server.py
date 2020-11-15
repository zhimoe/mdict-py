# -*- coding: utf-8 -*-
# version: python 3.5
import logging as log
import threading
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server, WSGIRequestHandler

from mdict_query import IndexBuilder
from mdx_util import *

CONTENT_TYPE_MAP = {
    'html': 'text/html; charset=utf-8',
    'js': 'application/x-javascript',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'mp3': 'audio/mpeg',
    'mp4': 'audio/mp4',
    'wav': 'audio/wav',
    'spx': 'audio/ogg',
    'ogg': 'audio/ogg',
    'eot': 'font/opentype',
    'svg': 'text/xml',
    'ttf': 'application/x-font-ttf',
    'woff': 'application/x-font-woff',
    'woff2': 'application/font-woff2',
}

try:
    base_path = os.path.dirname(sys.executable)
except Exception:
    log.warning("set base path failed, set current work dir as base path")
    base_path = os.path.abspath(".")

RESOURCE_DIR = os.path.join("./static/")
STATIC_MAP = get_static_map(RESOURCE_DIR, CONTENT_TYPE_MAP)

BUILDERS = dict()
HanDcit = "hycd_3rd" # 中文词典的名称
DICTS_MAP = {"LSC4": "./LSC4.mdx",
            #  "O8C": "./O8C.mdx",
             HanDcit: "./"+ HanDcit +".mdx"}


def build_dict() -> Dict[str, IndexBuilder]:
    """将所有词典构建好builders,根据前端选择查询对应的词典"""
    global BUILDERS
    for d, f in DICTS_MAP.items():
        if not os.path.exists(f):
            log.warning(f"the dict({d}) file:{f} doesn't exist,removed")
    for d, f in DICTS_MAP.items():
        _builder = IndexBuilder(f)
        BUILDERS[d] = _builder
    log.info(f"all dictionaries= {DICTS_MAP}")


def choose_dict(word, dict_option) -> str:
    """根据用户的输入单词和内容判断使用选择哪个单词"""
    option = "O8C"
    if dict_option:
        option = dict_option
    if is_chinese(word):
        option = HanDcit
    return option


def application(environ, start_response):
    """a wsgi application"""
    path_info = environ['PATH_INFO'].encode('iso8859-1').decode('utf-8')
    dict_option = environ['QUERY_STRING'].encode('iso8859-1').decode('utf-8')
    request_method = environ["REQUEST_METHOD"]
    remote_addr = environ["REMOTE_ADDR"]

    # process the static resource request
    if "GET" == request_method:
        if path_info == "/":
            path_info = "/index.html"

        if path_info in STATIC_MAP:
            static_file = STATIC_MAP[path_info]
            content_type = CONTENT_TYPE_MAP.get(get_file_ext(static_file), 'text/html; charset=utf-8')
            start_response('200 OK', [('Content-Type', content_type), ('Cache-Control', "max-age=72000")])
            return [read_all_bytes(static_file)]
        # 不在static目录下，但是是属于mdd文件的资源文件，去mdd builder下面查询
        # TODO: 无法判断当前的词典对应的mdd文件，所以不好判断
        # elif get_file_ext(path_info) in CONTENT_TYPE_MAP:
        #     content_type = CONTENT_TYPE_MAP.get(get_file_ext(path_info), 'text/html; charset=utf-8')
        #     start_response('200 OK', [('Content-Type', content_type)])
        #     return get_definition_mdd(path_info, builder)

        # 不在static目录内的静态资源一律忽略
        else:
            start_response('200 OK',
                           [('Content-Type', 'text/html; charset=utf-8'), ('Cache-Control', "max-age=72000")])
            return [b'']
    # 单词查询
    if "POST" == request_method:
        req_size = int(environ["CONTENT_LENGTH"])
        req_bytes = environ["wsgi.input"].read(req_size)
        params = {k: v[0] for k, v in parse_qs(req_bytes.decode("utf-8")).items()}  # {word:?,dict:?}
        word, dict_option = params.values()
        log.info(f"##### user {remote_addr} query {word} use dict={dict_option}")
        builder = BUILDERS[choose_dict(word, dict_option)]
        start_response("200 OK",
                       [('Content-Type', 'text/html; charset=utf-8'), ('Server', 'nginx')])
        return get_definition_mdx(word, builder)


class NoLoggingWSGIRequestHandler(WSGIRequestHandler):
    """disable the wsgi stderr logging"""

    def log_message(self, format, *args):
        pass


def web_server():
    """创建一个服务器，IP地址为空，端口是8080，处理函数是application,通过NoLoggingWSGIRequestHandler关闭wsgi的默认log"""
    httpd = make_server('', 8080, application, handler_class=NoLoggingWSGIRequestHandler)
    log.info("Serving HTTP on port 8080...")
    # 开始监听HTTP请求:
    httpd.serve_forever()


if __name__ == '__main__':
    log.getLogger().setLevel(log.DEBUG)
    build_dict()
    t = threading.Thread(target=web_server, args=())
    t.start()
