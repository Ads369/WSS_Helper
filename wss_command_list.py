"""-"""
from loguru import logger
from fuzzywuzzy import process
import wss_main_support_service as wss_main_support_service
import config._command_list as s_com_list

commands_dict = s_com_list.commands_dict


def main_handler_commands(com_str: str) -> None:
    """-"""
    logger.info(com_str)
    wss_main_support_service.to_clipboard(commands_dict[com_str])


def main():
    """-"""
    keys = commands_dict.keys()
    print(keys)


def fuzzy_search_commands(str_in: str):

    keys = commands_dict.keys()
    ratios = process.extract(str_in, keys)
    return ratios
    # You can also select the string with the highest matching percentage
    # highest = process.extractOne(str_in, keys)
    # print(highest)


if __name__ == "__main__":
    # main()
    fuzzy_search_commands("te v ad")
