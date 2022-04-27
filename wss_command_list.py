from loguru import logger
import wss_main_support_service
import config._command_list as s_com_list

commands_dict = s_com_list.commands_dict

def main_handler_commands(com_str:str) -> None:
    logger.info(com_str)
    wss_main_support_service.to_clipboard(commands_dict[com_str])


def main():
    keys = commands_dict.keys()
    print(keys)


if __name__ == '__main__':
    main()