import imp
import os
import datetime
import io

from configparser import ConfigParser

import common.helpers

from azure.storage.blob import BlobServiceClient
import azure.batch.models as batchmodels
from azure.batch import BatchServiceClient, batch_auth


def execute_batchapi(global_cfg: ConfigParser, params_cfg: ConfigParser):
    """Execute the batchapi with the specified Configuration

    Args:
        global_cfg (ConfigParser): the global configuration to use 
        params_cfg (ConfigParser): the specific configurations to use
    """

    batch_account_name = global_cfg.get("batch", "batch_account_name")

    common.helpers.print_configuration(global_cfg)


if __name__ == "__main__":

    global_cfg = ConfigParser()
    global_cfg.read(common.helpers.SAMPLE_CONFIG_FILE_NAME)

    params_cfg = ConfigParser()
    params_cfg.read(os.path.splitext(os.path.basename(__file__))[0] + ".cfg")

    execute_batchapi(global_cfg, params_cfg)
