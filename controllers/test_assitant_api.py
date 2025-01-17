"""
测试助手api
"""
from sanic import Blueprint

from common.res_decorator import async_json_resp
from services.test_assistant_service import convert_word_to_md

bp = Blueprint("testAssistant", url_prefix="/ta")


@bp.post("/word_to_md")
@async_json_resp
async def convert_doc_to_markdown_api(request):
    """
    转换word文档 markdown
    :param request:
    :return:
    """
    file_key = request.json.get("file_key")
    result = await convert_word_to_md(file_key)
    return result
