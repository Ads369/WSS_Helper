import re
from sqlalchemy import true
from tabulate import tabulate


def handler_block(str_in):
    """-"""
    strings_list = str_in.split("\n")

    res_str_list = []
    for string in strings_list:
        searc_f = re.search(r'.*<Field Name="([\w,\s,\-,\(,\),\:]+)".*', string)
        searc_i = re.search(r'.*Identity="(.*)" I.*', string)
        searc_r = re.search(r'.*IsRequired="true".*', string)
        res_str = ""

        if searc_i is not None:
            ident = searc_i.group(1)
        else:
            ident = "Строка"

        if searc_r is not None:
            is_req_str = "Да"
        else:
            is_req_str = "Нет"

        if searc_f is not None:
            field_name = searc_f.group(1)
            table_line = [field_name, ident, is_req_str]
            res_str_list.append(table_line)

    headers = ["Поле", "Идентификатор", "Обязательное"]

    result_str = tabulate(sorted(res_str_list), headers=headers)
    return result_str


def search_list(text_in, id=0):
    """-"""
    result_str = ""
    search_list = re.findall('<List.*?Code="(\d*?)".*>((.|\n)*?)</List>', text_in)

    for match in search_list:
        if id == 0 or match[0] == str(id):
            result_str += f"\n### {match[0]}:\n"
            result_str += f"{handler_block(match[1])}\n"

    print(result_str)


def read_file(is_work=True):
    """-"""
    if is_work:
        file_name = "program/Convert_XML_WebServicest_to_MD/work.txt"
    else:
        file_name = "program/Convert_XML_WebServicest_to_MD/test.txt"

    with open(file_name, "r", encoding="utf-8") as f:
        text = f.read()
    return text


def main():
    """-"""
    is_work = True
    doc_type = "17"

    text = read_file(is_work)
    search_list(text, doc_type)


if __name__ == "__main__":
    main()
