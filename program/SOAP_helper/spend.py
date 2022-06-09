import sys
from pathlib import Path

sys.path.append(str(Path(".").absolute()))
from config.load_cfg import config
from services import wss_webservices_controller_zeep as wws_ws

# Available methods:
#     AcceptDocumentSolution
#     CreateDocument
#     CreateElement
#     FindObjects
#     GetDocumentsByFields
#     GetFile
#     UpdateElement

wsszeep = wws_ws.WssZeep()


# param = wsszeep.get_param_accept_document_solution(
#     comment_to_solution = '',
#     emails_to_notify='',
#     reg_number='',
#     solution='',
#     user_email = '',
#     base_fields=[bdf])

param = wsszeep.get_param_get_document_by_fields(
    list_name="Users", searchable_field={"Имя пользователя": "Кижапкина Елена"}
)

param = wsszeep.get_param_get_document_by_fields(
    list_name="incomming_cok",
    searchable_field={
        "Регистрационный номер": "В-Гр-В-ТМН-2022-74134; В-Гр-В-ТМН-2022-74430"
    },
)

zeep_result = wsszeep.send_request("GetDocumentsByFields", param)
wsszeep.print_history()
