from urllib.parse import unquote
from sanic import Blueprint, Request

from common.minio_util import MinioUtils
from common.res_decorator import async_json_resp
from services.pandas_ai_service import read_excel, query_excel

bp = Blueprint("fileChatApi", url_prefix="/file")

minio_utils = MinioUtils()

"""
文件问答存在的问题:
1、生成的python脚本生成文本或图片无法确定
2、本地7b模型生成的稳定性差
"""


@bp.post("/read_file")
@async_json_resp
async def read_file(req: Request):
    """
    读取文件内容
    :param req:
    :return:
    """

    file_key = req.args.get("file_qa_str")
    if not file_key:
        file_key = req.json.get("file_qa_str")

    file_key = file_key.split("|")[0]  # 取文档地址

    file_url = minio_utils.get_file_url_by_key(object_key=file_key)
    result = await read_excel(file_url)
    return result


@bp.get("/query_excel")
@async_json_resp
async def process_query(req: Request):
    """

    :param req:
    :return:
    """
    query_str = unquote(req.query_string)
    if not query_str:
        return None

    try:
        str_split = query_str.replace("&", "").replace("=", "").split("@@@@")
        query_text = str_split[0]
        file_key = str_split[1]
        file_url = minio_utils.get_file_url_by_key(object_key=file_key)

        result = await query_excel(file_url, query_text)
        return result
    except IndexError:
        raise ValueError("Invalid query string format")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")


@bp.post("/upload_file")
@async_json_resp
async def upload_file(request: Request):
    """
    上传附件
    :param request:
    :return:
    """
    file_url = minio_utils.upload_file_from_request(request=request)
    return file_url
