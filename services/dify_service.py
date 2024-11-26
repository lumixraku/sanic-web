import json
import logging
import os
import re
import traceback
import uuid
from typing import Dict

import aiohttp

from common.exception import MyException
from constants.code_enum import (
    DiFyAppEnum,
    DataTypeEnum,
    DiFyCodeEnum,
    SysCodeEnum,
)
from services.db_qadata_process import process
from services.user_service import add_question_record


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

            uuid_str = str(uuid.uuid4())
            query = req_obj.get("query")
            #  使用正则表达式移除所有空白字符（包括空格、制表符、换行符等）
            cleaned_query = re.sub(r"\s+", "", query)
            source_chat = {
                "chat_id": uuid_str,
                "query": cleaned_query,
                "qa_type": req_obj.get("qa_type"),
            }

            # 获取登录用户信息
            token = res.request.headers.get("Authorization")
            if not token:
                raise MyException(SysCodeEnum.c_401)
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            # 封装问答上下文信息
            qa_context = QaContext(token, query, uuid_str)

            # 判断请求类别
            app_key = self._get_authorization_token(source_chat)

            # 构建请求参数
            dify_service_url, body_params, headers = self._build_request(source_chat["query"], app_key)

            async with aiohttp.ClientSession(read_bufsize=1024 * 16) as session:
                async with session.post(
                    dify_service_url,
                    headers=headers,
                    json=body_params,
                    timeout=aiohttp.ClientTimeout(total=60 * 2),  # 等待2分钟超时
                ) as response:
                    logging.info(f"dify response status: {response.status}")
                    if response.status == 200:
                        await self.res_begin(res, uuid_str)
                        data_type = ""
                        bus_data = ""
                        while True:
                            reader = response.content
                            reader._high_water = 10 * 1024 * 1024  # 设置为10MB
                            chunk = await reader.readline()
                            if not chunk:
                                break
                            str_chunk = chunk.decode("utf-8")
                            if str_chunk.startswith("data"):
                                str_data = str_chunk[5:]
                                data_json = json.loads(str_data)
                                event_name = data_json.get("event")
                                if DiFyCodeEnum.MESSAGE.value[0] == event_name:
                                    answer = data_json.get("answer")
                                    if answer and answer.startswith("dify_"):
                                        event_list = answer.split("_")
                                        if event_list[1] == "0":
                                            # 输出开始
                                            data_type = event_list[2]
                                            if data_type == DataTypeEnum.ANSWER.value[0]:
                                                await self.send_message(res, qa_context, {"data": {"messageType": "begin"}, "dataType": data_type})
                                        elif event_list[1] == "1":
                                            # 输出结束
                                            data_type = event_list[2]
                                            if data_type == DataTypeEnum.ANSWER.value[0]:
                                                await self.send_message(res, qa_context, {"data": {"messageType": "end"}, "dataType": data_type})

                                            # 输出业务数据
                                            elif bus_data and data_type == DataTypeEnum.BUS_DATA.value[0]:
                                                res_data = process(json.loads(bus_data)["data"])
                                                # logging.info(f"chart_data: {res_data}")
                                                await self.send_message(
                                                    res,
                                                    qa_context,
                                                    {"data": res_data, "dataType": data_type},
                                                )

                                            data_type = ""

                                    elif len(data_type) > 0:
                                        # 这里输出 t02之间的内容
                                        if data_type == DataTypeEnum.ANSWER.value[0]:
                                            await self.send_message(
                                                res,
                                                qa_context,
                                                {"data": {"messageType": "continue", "content": answer}, "dataType": data_type},
                                            )

                                        # 这里设置业务数据
                                        if data_type == DataTypeEnum.BUS_DATA.value[0]:
                                            bus_data = answer
        except Exception as e:
            logging.error(f"Error during get_answer: {e}")
            traceback.print_exception(e)
            return {"error": str(e)}  # 返回错误信息作为字典
        finally:
            await self.res_end(res)

    @staticmethod
    async def send_message(response, qa_context, message):
        """
            SSE 格式发送数据，每一行以 data: 开头
        :param response:
        :param qa_context
        :param message:
        :return:
        """
        await response.write("data:" + json.dumps(message, ensure_ascii=False) + "\n\n")

        # 保存用户问答记录 1.保存用户问题 2.保存用户答案 t02 和 t04
        if "content" in message["data"]:
            await add_question_record(qa_context.token, qa_context.chat_id, qa_context.question, message, "")
        elif message["dataType"] == DataTypeEnum.BUS_DATA.value[0]:
            await add_question_record(qa_context.token, qa_context.chat_id, qa_context.question, "", message)

    @staticmethod
    async def res_begin(res, uuid_str):
        """

        :param res:
        :param uuid_str:
        :return:
        """
        await res.write(
            "data:"
            + json.dumps(
                {
                    "data": {"id": uuid_str},
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
    def _build_request(query, app_key):
        """
        构建请求参数
        :param app_key:
        :param query:
        :return:
        """
        body_params = {
            "inputs": {},
            "query": query,
            "response_mode": "streaming",
            "user": "abc-123",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {app_key.value[1]}",
        }

        if os.getenv("ENV") == "test":
            dify_service_url = os.getenv("DIFY_SERVICE_URL_TEST")
        else:
            dify_service_url = os.getenv("DIFY_SERVICE_URL_DEV")

        return dify_service_url, body_params, headers

    @staticmethod
    def _get_authorization_token(source_chat: Dict):
        """
            根据请求类别获取api/token
            :param source_chat
        :return:
        """
        qa_type = source_chat["qa_type"]
        if qa_type == DiFyAppEnum.DATABASE_QA.value[0]:
            return DiFyAppEnum.DATABASE_QA
        if qa_type == DiFyAppEnum.FILEDATA_QA.value[0]:
            return DiFyAppEnum.FILEDATA_QA
        else:
            raise ValueError("问答类型不支持")
