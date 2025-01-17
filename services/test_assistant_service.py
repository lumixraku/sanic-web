import base64
import os
from io import BytesIO

import mammoth
import markdownify
import requests

from common.exception import MyException
from common.minio_util import MinioUtils
from constants.code_enum import SysCodeEnum


def convert_img(image):
    """
    将Word文档中的图片转换为Markdown中可以使用的链接或嵌入内容。
    :param image:
    :return: 图片标签字典
    """
    with image.open() as image_bytes:
        return {"src": ""}
        # return {"src": "data:{0};base64,{1}".format(image.content_type, base64.b64encode(image_bytes.read()).decode())}


async def convert_word_to_md(file_key):
    """

    :param file_key:
    :return:
    """
    html_path = file_key + "_to_html.html"
    docx_filename = file_key + ".docx"

    try:
        # 获取文件URL
        file_url = MinioUtils().get_file_url_by_key(object_key=file_key)

        # 从URL下载Word文档并读取其内容
        response = requests.get(file_url)
        response.raise_for_status()  # 检查请求是否成功

        # 使用BytesIO来处理内存中的二进制数据流，避免创建临时文件
        docx_content = BytesIO(response.content)

        # 转化Word文档为HTML和Markdown
        result = mammoth.convert_to_html(docx_content, convert_image=mammoth.images.img_element(convert_img))
        html = result.value
        md = markdownify.markdownify(html, heading_style="ATX")

        messages = result.messages
        if messages:
            for message in messages:
                print(f"警告或错误信息: {message}")

        return md  # 直接返回Markdown文本

    except requests.RequestException as e:
        print(f"请求文件时发生错误：{e}")
        raise MyException(SysCodeEnum.c_9999)
    except Exception as e:
        print(f"转换过程中发生错误：{e}")
        raise MyException(SysCodeEnum.c_9999)
    finally:
        # 清理临时文件
        for path in [html_path, docx_filename]:
            if os.path.exists(path):
                os.remove(path)
