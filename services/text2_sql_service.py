import io
import json
import logging

import duckdb
import pandas as pd
import requests

from common.date_util import DateEncoder
from common.exception import MyException
from common.minio_util import MinioUtils
from common.mysql_util import MysqlUtil
from constants.code_enum import SysCodeEnum as SysCode

logger = logging.getLogger(__name__)


async def exe_sql_query(model_out_str):
    """
    执行大模型解析出的sql语句并返回结果集
    Args:
        model_out_text 大模型输出信息
    Return:
    """

    if model_out_str:
        try:
            model_out_json = json.loads(model_out_str)
            if not isinstance(model_out_json, dict):
                model_out_json = json.loads(model_out_json)
            sql = model_out_json["sql"]
            if sql:
                result = MysqlUtil().query_ex(sql)
                table_schema_dict = MysqlUtil().get_multiple_tables_column_comments(["view_alarm_detail"])
                table_schema_dict["llm"] = model_out_json
                table_schema_dict["data"] = result
                return json.dumps(table_schema_dict, ensure_ascii=False, cls=DateEncoder)
            else:
                logger.error("数据应答大模型返回SQL语句为空")
                raise MyException(SysCode.c_9999)
        except Exception as e:
            logger.error(f"数据应答处理失败: {model_out_str} {e}")
            raise MyException(SysCode.c_9999)
    else:
        logger.error("数据应答大模型返回结果为空")
        raise MyException(SysCode.c_9999)


async def exe_file_sql_query(file_key, model_out_str):
    """
    文件问答: 执行大模型解析出的SQL语句并返回结果集

    Args:
        file_key (str): 文件key
        model_out_str (str): 大模型输出信息

    Returns:
        dict: {"column":[], "result":[]}

    Raises:
        MyException: 当文件问答大模型返回结果为空或SQL语句为空时抛出异常
    """
    if not model_out_str:
        logger.error("文件问答大模型返回结果为空")
        raise MyException(SysCode.c_9999)

    try:
        # 获取文件URL
        file_url = MinioUtils().get_file_url_by_key(object_key=file_key)
        extension = file_key.split(".")[-1].lower()

        # 根据文件类型读取数据
        if extension in ["xlsx", "xls"]:
            response = requests.get(file_url)
            df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
        elif extension == "csv":
            df = pd.read_csv(file_url)
        else:
            logger.error(f"不支持的文件扩展名: {extension}")
            raise MyException(SysCode.c_9999)

        # 连接到DuckDB (这里使用内存数据库) 并注册DataFrame
        con = duckdb.connect(database=":memory:")
        con.register("excel_table", df)

        # 解析模型输出并获取SQL语句
        model_out_json = json.loads(model_out_str)
        sql = model_out_json.get("sql", "").replace("`", "")  # 移除反引号以避免SQL语法错误

        if not sql.strip():
            logger.error("文件问答大模型返回SQL语句为空")
            raise MyException(SysCode.c_9999)

        # 执行SQL查询
        cursor = con.execute(sql)

        # 获取列名称和查询结果的数据行
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # 构建结果字典
        result = [dict(zip(columns, row)) for row in rows]

        return json.dumps({"llm": model_out_json, "data": {"column": columns, "result": result}}, ensure_ascii=False, cls=DateEncoder)

    except Exception as e:
        logger.error(f"文件问答处理失败: {model_out_str}, Error: {e}")
        raise MyException(SysCode.c_9999)
