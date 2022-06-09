import sys
import importlib.util
import os
import urllib3
import yaml
from loguru import logger

# Import module from path
spec = importlib.util.spec_from_file_location(
    "wss_webservice_controller", "services/wss_webservices_controller_zeep.py"
)
wss_ws_z = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wss_ws_z)

# Logger setup
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("program/AccessSolution/logs/log_full.log", level="DEBUG")

# Disable Warning by urllib3
urllib3.disable_warnings()

# Get security data
with open(r"config/config.yaml", encoding="utf8") as f:
    config = yaml.safe_load(f)

# Get path for Docs list (.txt)
path_documents_list = (
    os.getcwd() + "/program/AccessSolution/accept_solution_documents_list.txt"
)

GOOD_RESULT = 0
BAD_RESULT = 0

# Count lines
with open(path_documents_list, "r", encoding="utf-8") as fp:
    count = None
    for count, line in enumerate(fp):
        pass
total_lines = count + 1
SELECT_LINE = 0

# init zeep client
wsszeep = wss_ws_z.WssZeep()

# Main loop
for line in open(path_documents_list, encoding="utf-8"):
    SELECT_LINE += 1
    reg_num = line.strip()

    # TEST
    # bdf = wsszeep.get_base_document_field('Содержание','Здесь был тест2')
    # file = wsszeep.get_file_document_field(
    #     field_name='Файлы поручения',
    #     file_name='qwe.png',
    #     base64_str='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2N'\
    #         'gYAAAAAMAAWgmWQ0AAAAASUVORK5CYII='.encode('UTF-8')
    #     )

    # WORK
    # bdf = wsszeep.get_base_document_field('Статус','Здесь был тест2')
    u1 = wsszeep.get_lookup_document_field("Инициатор", "id", "10879")
    u2 = wsszeep.get_lookup_document_field("Автор поручения", "id", "10879")

    param = wsszeep.get_param_accept_document_solution(
        comment_to_solution="SD383752",
        # emails_to_notify='',
        emails_to_notify="",
        reg_number=reg_num,
        # solution='Разослать',
        solution="Техническое решение",
        user_email=config["accept_solution"]["ads_email"],
        # base_fields=[bdf],
        # files_files=[file],
        base_fields=[u1, u2],
    )
    zeep_result = wsszeep.send_request("AcceptDocumentSolution", param)
    # wsszeep.print_history()

    if zeep_result:
        GOOD_RESULT += 1
        logger.info(f"({total_lines}/{SELECT_LINE}) {reg_num} +")
    else:
        BAD_RESULT += 1
        logger.info(f"({total_lines}/{SELECT_LINE}) {reg_num} -")

logger.info(f"Good: {GOOD_RESULT}, Bad: {BAD_RESULT}")
