import sys
from pathlib import Path

sys.path.append(str(Path(".").absolute()))
from services import wss_webservices_controller_zeep as wss_ws
from config.load_cfg import config


# def test_get_document_by_field():
#     xml = wws_ws.test_1()
#     assert len(xml) > 0


def test_get_document_by_field_default():
    """-"""
    wsszeep = wss_ws.WssZeep()
    param = wsszeep.get_param_get_document_by_fields()
    zeep_result = wsszeep.send_request("GetDocumentsByFields", param)
    temp_result = zeep_result["Documents"]["SearchedDocument"][0]["Fields"][
        "BaseSearchedDocumentField"
    ]
    value_name = wsszeep.find_value_by_field_name(temp_result, "Имя пользователя")
    assert value_name == "Кижапкина Елена"


if __name__ == "__main__":
    test_get_document_by_field_default()
