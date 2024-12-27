import json
import logging
import os
import re
import traceback

import aiohttp
import requests

from common.exception import MyException
from constants.code_enum import (
    DiFyAppEnum,
    DataTypeEnum,
    DiFyCodeEnum,
    SysCodeEnum,
)
from constants.dify_rest_api import DiFyRestApi
from services.db_qadata_process import process
from services.user_service import add_question_record, query_user_qa_record

logger = logging.getLogger(__name__)


class QaContext:
    """问答上下文信息"""

    def __init__(self, token, question, chat_id):
        self.token = token
        self.question = question
        self.chat_id = chat_id


class DiFyRequest:
    """
    DiFy操作服务类
    """

    def __init__(self):
        pass

    async def exec_query(self, res):
        """

        :return:
        """
        try:
            # 获取请求体内容 从res流对象获取request-body
            req_body_content = res.request.body
            # 将字节流解码为字符串
            body_str = req_body_content.decode("utf-8")

            req_obj = json.loads(body_str)
            logging.info(f"query param: {body_str}")

            # str(uuid.uuid4())
            chat_id = req_obj.get("chat_id")
            qa_type = req_obj.get("qa_type")

            #  使用正则表达式移除所有空白字符（包括空格、制表符、换行符等）
            query = req_obj.get("query")
            cleaned_query = re.sub(r"\s+", "", query)

            # 获取登录用户信息
            token = res.request.headers.get("Authorization")
            if not token:
                raise MyException(SysCodeEnum.c_401)
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            # 封装问答上下文信息
            qa_context = QaContext(token, query, chat_id)

            # 判断请求类别
            app_key = self._get_authorization_token(qa_type)

            # 构建请求参数
            dify_service_url, body_params, headers = self._build_request(cleaned_query, app_key, qa_type)

            async with aiohttp.ClientSession(read_bufsize=1024 * 16) as session:
                async with session.post(
                    dify_service_url,
                    headers=headers,
                    json=body_params,
                    timeout=aiohttp.ClientTimeout(total=60 * 2),  # 等待2分钟超时
                ) as response:
                    logging.info(f"dify response status: {response.status}")
                    if response.status == 200:
                        await self.res_begin(res, chat_id)
                        data_type = ""
                        bus_data = ""
                        while True:
                            reader = response.content
                            reader._high_water = 10 * 1024 * 1024  # 设置为10MB
                            chunk = await reader.readline()
                            if not chunk:
                                break
                            str_chunk = chunk.decode("utf-8")
                            print(str_chunk)
                            if str_chunk.startswith("data"):
                                str_data = str_chunk[5:]
                                data_json = json.loads(str_data)
                                event_name = data_json.get("event")
                                conversation_id = data_json.get("conversation_id")
                                message_id = data_json.get("message_id")
                                task_id = data_json.get("task_id")

                                if DiFyCodeEnum.MESSAGE.value[0] == event_name:
                                    answer = data_json.get("answer")
                                    if answer and answer.startswith("dify_"):
                                        event_list = answer.split("_")
                                        if event_list[1] == "0":
                                            # 输出开始
                                            data_type = event_list[2]
                                            if data_type == DataTypeEnum.ANSWER.value[0]:
                                                await self.send_message(
                                                    res,
                                                    qa_context,
                                                    {"data": {"messageType": "begin"}, "dataType": data_type},
                                                    qa_type,
                                                    conversation_id,
                                                    message_id,
                                                    task_id,
                                                )
                                        elif event_list[1] == "1":
                                            # 输出结束
                                            data_type = event_list[2]
                                            if data_type == DataTypeEnum.ANSWER.value[0]:
                                                await self.send_message(
                                                    res,
                                                    qa_context,
                                                    {"data": {"messageType": "end"}, "dataType": data_type},
                                                    qa_type,
                                                    conversation_id,
                                                    message_id,
                                                    task_id,
                                                )

                                            # 输出业务数据
                                            elif bus_data and data_type == DataTypeEnum.BUS_DATA.value[0]:
                                                res_data = process(json.loads(bus_data)["data"])
                                                # logging.info(f"chart_data: {res_data}")
                                                await self.send_message(
                                                    res,
                                                    qa_context,
                                                    {"data": res_data, "dataType": data_type},
                                                    qa_type,
                                                    conversation_id,
                                                    message_id,
                                                    task_id,
                                                )

                                            data_type = ""

                                    elif len(data_type) > 0:
                                        # 这里输出 t02之间的内容
                                        if data_type == DataTypeEnum.ANSWER.value[0]:
                                            await self.send_message(
                                                res,
                                                qa_context,
                                                {"data": {"messageType": "continue", "content": answer}, "dataType": data_type},
                                                qa_type,
                                                conversation_id,
                                                message_id,
                                                task_id,
                                            )

                                        # 这里设置业务数据
                                        if data_type == DataTypeEnum.BUS_DATA.value[0]:
                                            bus_data = answer

                                elif DiFyCodeEnum.MESSAGE_ERROR.value[0] == event_name:
                                    # 输出异常情况日志
                                    error_msg = data_json.get("message")
                                    logging.error(f"Error during get_answer: {error_msg}")

        except Exception as e:
            logging.error(f"Error during get_answer: {e}")
            traceback.print_exception(e)
            return {"error": str(e)}  # 返回错误信息作为字典
        finally:
            await self.res_end(res)

    @staticmethod
    async def send_message(response, qa_context, message, qa_type, conversation_id, message_id, task_id):
        """
            SSE 格式发送数据，每一行以 data: 开头
        :param response:
        :param qa_context
        :param message:
        :param qa_type
        :param conversation_id
        :param message_id
        :param task_id
        :return:
        """
        await response.write("data:" + json.dumps(message, ensure_ascii=False) + "\n\n")

        # 保存用户问答记录 1.保存用户问题 2.保存用户答案 t02 和 t04
        if "content" in message["data"]:
            await add_question_record(
                qa_context.token, conversation_id, message_id, task_id, qa_context.chat_id, qa_context.question, message, "", qa_type
            )
        elif message["dataType"] == DataTypeEnum.BUS_DATA.value[0]:
            await add_question_record(
                qa_context.token, conversation_id, message_id, task_id, qa_context.chat_id, qa_context.question, "", message, qa_type
            )

    @staticmethod
    async def res_begin(res, chat_id):
        """

        :param res:
        :param chat_id:
        :return:
        """
        await res.write(
            "data:"
            + json.dumps(
                {
                    "data": {"id": chat_id},
                    "dataType": DataTypeEnum.TASK_ID.value[0],
                }
            )
            + "\n\n"
        )

    @staticmethod
    async def res_end(res):
        """
        :param res:
        :return:
        """
        await res.write(
            "data:"
            + json.dumps(
                {
                    "data": "DONE",
                    "dataType": DataTypeEnum.STREAM_END.value[0],
                }
            )
            + "\n\n"
        )

    @staticmethod
    def _build_request(query, app_key, qa_type):
        """
        构建请求参数
        :param app_key:
        :param query: 用户问题
        :param qa_type: 问答类型
        :return:
        """
        body_params = {
            "query": query,
            "inputs": {"qa_type": qa_type},
            "response_mode": "streaming",
            "user": "abc-123",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {app_key}",
        }

        dify_service_url = DiFyRestApi.build_url(DiFyRestApi.DIFY_REST_CHAT)
        return dify_service_url, body_params, headers

    @staticmethod
    def _get_authorization_token(qa_type: str):
        """
            根据请求类别获取api/token
            固定走一个dify流
             app-IzudxfuN8uO2bvuCpUHpWhvH master分支默认的数据问答key
            :param qa_type
        :return:
        """
        # 遍历枚举成员并检查第一个元素是否与测试字符串匹配
        for member in DiFyAppEnum:
            if member.value[0] == qa_type:
                return os.getenv("DIFY_DATABASE_QA_API_KEY")
        else:
            raise ValueError(f"问答类型 '{qa_type}' 不支持")


async def query_dify_suggested(chat_id) -> dict:
    """
    发送反馈给指定的消息ID。

    :param chat_id: 消息的唯一标识符。
    :return: 返回服务器响应。
    """
    # 查询对话记录
    qa_record = query_user_qa_record(chat_id)
    url = DiFyRestApi.replace_path_params(DiFyRestApi.DIFY_REST_SUGGESTED, {"message_id": chat_id})
    api_key = os.getenv("DIFY_DATABASE_QA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.get(url + "?user=abc-123", headers=headers)
    print(response.text)

    # 检查请求是否成功
    if response.status_code == 200:
        logger.info("Feedback successfully sent.")
        return response.json()
    else:
        logger.error(f"Failed to send feedback. Status code: {response.status_code},Response body: {response.text}")
        raise
