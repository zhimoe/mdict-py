import os

from starlette.datastructures import Headers
from starlette.responses import (
    FileResponse,
    Response,
)
from starlette.staticfiles import StaticFiles, NotModifiedResponse
from starlette.types import Scope


class CachedStaticFiles(StaticFiles):
    """
    重写静态文件服务
    """

    def file_response(
            self,
            full_path: str,
            stat_result: os.stat_result,
            scope: Scope,
            status_code: int = 200,
    ) -> Response:
        method = scope["method"]
        request_headers = Headers(scope=scope)

        response = FileResponse(
            full_path, status_code=status_code, stat_result=stat_result, method=method
        )
        response.headers['Cache-Control'] = "max-age=720"
        if self.is_not_modified(response.headers, request_headers):
            return NotModifiedResponse(response.headers)
        return response

