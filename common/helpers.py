from configparser import ConfigParser
import datetime
import os


SAMPLE_CONFIG_FILE_NAME = "configuration.cfg"


def print_configuration(config: ConfigParser):
    """print the Configuration

    Args:
        config (ConfigParser): the Configuration
    """
    configuration_dict = {s: dict(config.items(s))
                          for s in config.sections()}
    print("----------------------")
    print(configuration_dict)


def generate_unique_resource_name(resource_prefix: str) -> str:
    """create a unique resource name by appending time

    Args:
        resource_prefix (str): prefix of the resource

    Returns:
        str: a speciffied resource name
    """
    return resource_prefix + "-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S%f")


# def wrap_commands_in_shell(os_type: str, commands: list(str)) -> str:
#     """_summary_

#     Args:
#         ostype (str): _description_
#         commands (list): _description_

#     Returns:
#         str: _description_
#     """
#     if os_type.lower() == "linux":
#         return (f'/bin/bash -c '
#                 f'\'set -e; set -o pipfail; {";".join(commands)}; wait\'')
#     elif os_type.lower() == "windows":
#         return f'cmd.exe /c "{"&".join(commands)}"'
#     else:
#         raise ValueError(f'unkown os type: {os_type}')
