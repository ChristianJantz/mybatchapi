from configparser import ConfigParser
import os


SAMPLE_CONFIG_FILE_NAME = "configuration.cfg"


def print_configuration(config: ConfigParser):
    """print the Configuration

    Args:
        config (ConfigParser): the Configuration
    """
    configuration_dict = {s: dict(config.items(s))
                          for s in config.sections() + ['default']}
    print("----------------------")
    print(configuration_dict)
