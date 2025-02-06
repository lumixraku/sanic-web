import pymysql
import os

from pymysql import MySQLError

"""
Mysql 初始化脚本工具类
"""

# 配置信息
MYSQL_ROOT_PASSWORD = "1"  # MySQL root 用户的密码
SQL_FILE = "../docker/init_sql.sql"  # SQL 文件路径
HOST = "localhost"  # MySQL 服务器地址
PORT = 13006  # MySQL 服务器端口


def check_sql_file(file_path):
    """
    检查 SQL 文件是否存在
    :param file_path:
    :return:
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Error: SQL file {file_path} not found.")


def execute_sql_file(file_path):
    """
    执行 SQL 文件
    :param file_path:
    :return:
    """
    try:
        # 创建数据库连接
        connection = pymysql.connect(
            host=HOST, user="root", password=MYSQL_ROOT_PASSWORD, port=PORT, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            print(f"Initializing MySQL with {file_path} on port {PORT}...")

            # 读取 SQL 文件
            with open(file_path, "r", encoding="utf-8") as file:
                sql_script = file.read()

            # 分割 SQL 命令并执行
            commands = sql_script.split(";")
            for command in commands:
                if command.strip():  # 忽略空命令
                    cursor.execute(command)

            # 提交事务
            connection.commit()
            print("MySQL initialization completed successfully.")
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        if connection.open:
            connection.close()


def execute_user_qa_record_sql():
    """
    使用 pymysql 连接数据库并执行 SQL 语句。
    初始化特殊结构json数据
    """

    sql_insert_data = """
    INSERT INTO chat_db.t_user_qa_record
    (id, user_id, conversation_id,message_id,task_id,chat_id, question, to2_answer, to4_answer, qa_type,file_key,create_time)
    VALUES(%s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s,%s);
    """

    data_to_insert = [
        (
            305,
            1,
            "0d4691fd-2143-4656-adff-0f573360eb17",
            "90331784-ab3f-4076-b3e3-55ea0f4b75b5",
            "d6398d9e-d6ae-475c-91cd-1a84d0af6af9",
            "f16a1970-8001-4763-bc1a-6d6b9a2ed429",
            "统计案件数量按分局分组柱状图",
            '{"data": {"messageType": "continue", "content": "> 好，我现在需要分析给定的诈骗数据，并总结出数据趋势。首先，我会仔细查看数据内容。数据中有两个主要字段：'
            "所属分局"
            "和"
            "总数"
            "。每个结果都是一个字典，包含一个 "
            "所属分局"
            " 和对应的 "
            "总数"
            '。我的任务是从这些数据中提取趋势信息。接下来，我会列出所有诈骗案件的分布情况：- 浦东分局：7起- 朝阳分局：4起- 天河分局：4起- 南山分局：3起- 武侯分局：1起- 锦江分局：2起- 徐汇分局：10起- 海淀分局：4起- 白云分局：3起- 福田分局：2起现在，我需要找出主要的趋势。首先，徐汇分局的案件数最高，达到了10起。这可能意味着该地区的诈骗活动较为频繁或严重。其次，浦东分局紧随其后，共7起。朝阳、天河、海淀和白云分局各有4起，而南山、锦江、武侯和福田则较少，分别有3、2、1和2起。从这些数据可以看出，诈骗案件主要集中在徐汇、浦东以及朝阳、天河等区域。其他地区的案件数相对较少，但也不为零。综上所述，诈骗案件数量在徐汇分局最高，其次是浦东分局。其他地区的案件数较低，但分布较为广泛。\\n\\n诈骗案件数量主要集中在徐汇分局，其次为浦东分局，朝阳分局和天河分局各有4起，而南山区、锦江区、武侯区和福田区的案件数较少。详情如下图:"}, "dataType": "t02"}',
            '{"data": {"chart_type": "柱状图", "template_code": "temp03", "data": [["product", "总数"], ["浦东分局", "7"], ["朝阳分局", "4"], ["天河分局", "4"], ["南山分局", "3"], ["武侯分局", "1"], ["锦江分局", "2"], ["徐汇分局", "10"], ["海淀分局", "4"], ["白云分局", "3"], ["福田分局", "2"]], "note": "数据来源: xxx数据库，以上数据仅供参考，具体情况可能会根据xx进一步调查和统计而有所变化"}, "dataType": "t04"}',
            "DATABASE_QA",
            "",
            "2025-02-06 02:15:53",
        ),
        (
            306,
            1,
            "932217c4-0dea-4884-8d78-ebdc2e2aee9d",
            "46f6f59d-2eaf-4541-a5e2-ee76a971b03b",
            "89bbc35a-2318-43d2-a622-fef8886f92b2",
            "2e892a1b-a00e-45a8-b786-69027d8ac17f",
            "统计案件数量按月分组折线图",
            '{"data": {"messageType": "continue", "content": "> 好的，我现在需要分析用户提供的诈骗数据，并总结出其中的趋势。首先，我会仔细查看数据内容。数据中的月份是从2024年1月到2024年12月，每个月的案件数量分别是：5,4,3,2,1,5,4,3,2,1,5,5。看起来是有一个波动的趋势。接下来，我会观察这些数字的变化。前几个月（1月到5月）的案件数量逐渐减少，从5降到1。然后到了6月又回升到5，7月降到4，8月降到3，9月降到2，10月降到1，接着在11月和12月又回到5。这种趋势显示出一个周期性的变化：前半年案件数量持续下降，后半年则开始上升并保持稳定。这可能与某些外部因素有关，比如政策调整、经济状况变化或季节性因素导致诈骗活动的波动。此外，数据中的低谷出现在每年的中期（第6个月），之后又逐渐恢复到较高的水平。这种周期性的模式可以帮助预测未来的案件数量，以便采取相应的防范措施。总结来说，诈骗案件数量呈现明显的半年度周期，前半年下降后半年回升稳定。\\n\\n诈骗案件数量呈现出明显的周期性波动趋势。具体表现为：\\n\\n1. **半年度下降**：从2024年1月到6月，案件数量逐渐减少，分别从5降至1。\\n2. **半年度回升**：从7月开始，案件数量再次上升至5，并在随后的8、9、10月份逐步降至3、2、1。\\n3. **稳定波动**：11月和12月的案件数量保持在5个单位。\\n\\n这种趋势显示出诈骗案件数量在半年内呈现下降后半年回升并趋于稳定的周期性变化。详情如下图:"}, "dataType": "t02"}',
            '{"data": {"chart_type": "折线图", "template_code": "temp04", "data": [["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"], ["5", "4", "3", "2", "1", "5", "4", "3", "2", "1", "5", "5"]], "note": "数据来源: xxx数据库，以上数据仅供参考，具体情况可能会根据xx进一步调查和统计而有所变化"}, "dataType": "t04"}',
            "DATABASE_QA",
            "",
            "2025-02-06 02:17:06",
        ),
        (
            307,
            1,
            "ab6fa2e8-3199-4d97-9d9c-4433a63521c0",
            "817a3d00-1894-43b7-b7da-d8fcdbc19fa5",
            "34877aae-a7eb-4765-a23d-0ed8f6d08b4f",
            "1bc014e1-0c37-4ac1-9292-e05f2ac89d31",
            "统计案件数量按分局分组饼图",
            '{"data": {"messageType": "continue", "content": "> 好的，我现在需要分析给定的诈骗数据，并总结出其中的趋势。首先，我会仔细查看数据内容。数据中的结果是一个列表，每个元素包含“所属分局”和“总数”。我需要统计每个分局的总数，然后观察是否有明显的趋势或模式。从数据来看：- 浦东分局有7起案件，- 朝阳、天河、海淀、白云、福田各4、3、2、3、2起，- 武侯、锦江、徐汇各有1、2、10起。注意到徐汇分局的总数高达10，远超过其他分局。这可能意味着徐汇分局是诈骗案件的主要发源地或高发区。而武侯和锦江只有少数案件，可能属于较少见的情况。接下来，我会考虑这些数据是否反映了某种地理分布的趋势，比如某些区域更容易发生诈骗。此外，总数较高的徐汇可能需要特别关注，因为它可能涉及更严重的诈骗活动。最后，总结时会指出徐汇分局的高发情况，并建议进一步调查该地区的诈骗原因。\\n\\n根据提供的诈骗数据，我们可以观察到以下趋势：\\n\\n1. **案件数量分布**：各分局的诈骗案件数量不均，徐汇分局以10起案件最多，显著高于其他区域。\\n\\n2. **地区集中性**：部分区域如徐汇分局呈现较高的诈骗发生率，可能暗示该地区的诈骗活动较为活跃或集中。\\n\\n3. **案例少的区域**：武侯和锦江分局仅有少数案件，表明这些地区的诈骗活动较少见。\\n\\n综上所述，诈骗案件主要集中在徐汇分局，其他区域则相对较少。建议进一步关注高发区域以预防和打击诈骗活动。详情如下图:"}, "dataType": "t02"}',
            '{"data": {"chart_type": "饼图", "template_code": "temp02", "data": [{"name": "浦东分局", "value": "7", "percent": false}, {"name": "朝阳分局", "value": "4", "percent": false}, {"name": "天河分局", "value": "4", "percent": false}, {"name": "南山分局", "value": "3", "percent": false}, {"name": "武侯分局", "value": "1", "percent": false}, {"name": "锦江分局", "value": "2", "percent": false}, {"name": "徐汇分局", "value": "10", "percent": false}, {"name": "海淀分局", "value": "4", "percent": false}, {"name": "白云分局", "value": "3", "percent": false}, {"name": "福田分局", "value": "2", "percent": false}], "note": "数据来源: xxx数据库，以上数据仅供参考，具体情况可能会根据xx进一步调查和统计而有所变化"}, "dataType": "t04"}',
            "DATABASE_QA",
            "",
            "2025-02-06 02:23:51",
        ),
    ]

    # 创建数据库连接
    connection = pymysql.connect(
        host=HOST, user="root", password=MYSQL_ROOT_PASSWORD, port=PORT, db="chat_db", charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # 使用 executemany 方法插入多条数据
            cursor.executemany(sql_insert_data, data_to_insert)
        # 提交事务
        connection.commit()
    except MySQLError as e:
        print(f"Error executing query: {e}")
        # 如果出现错误，则回滚事务
        if connection.open:
            connection.rollback()
    finally:
        # 关闭数据库连接
        connection.close()


if __name__ == "__main__":
    check_sql_file(SQL_FILE)
    execute_sql_file(SQL_FILE)
    execute_user_qa_record_sql()
