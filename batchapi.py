
import os
import datetime
import io

from configparser import ConfigParser

import common.helpers

from azure.storage.blob import BlobServiceClient
import azure.batch.models as batchmodels
from azure.batch import BatchServiceClient, batch_auth


def creat_pool_if_not_exists(batch_service_client: BatchServiceClient, blob_service_client: BlobServiceClient, pool_id: str, params: ConfigParser, envs: list = None):
    """_summary_

    Args:
        batch_service_client (BatchServiceClient): _description_
        pool_id (str): _description_
        params (ConfigParser): _description_
        envs (list, optional): _description_. Defaults to None.
    """
    vm_config = batchmodels.VirtualMachineConfiguration(
        image_reference=batchmodels.ImageReference(
            publisher=params.get("vmpool", "publisher"),
            offer=params.get("vmpool", "offer"),
            sku=params.get("vmpool", "sku"),
            version="latest"
        ),
        node_agent_sku_id=params.get("vmpool", "node_agent_sku_id"),
        node_placement_configuration=batchmodels.NodePlacementConfiguration(
            policy="Regional"
        )
    )
    mounts = [
        batchmodels.MountConfiguration(
            azure_blob_file_system_configuration=batchmodels.AzureBlobFileSystemConfiguration(
                account_key=blob_service_client.credential.account_key,
                account_name=blob_service_client.account_name,
                container_name=params.get(
                    "mounts", "storage_mount_container_name"),
                relative_mount_path="{}-{}".format(blob_service_client.account_name, params.get(
                    "mounts", "storage_mount_container_name")),
                blobfuse_options=params.get("mounts", "blobfuseoptions")
            )
        ),
        batchmodels.MountConfiguration(
            nfs_mount_configuration=batchmodels.NFSMountConfiguration(
                source="{0}.blob.core.windows.net:/{1}/{2}".format(
                    blob_service_client.account_name, blob_service_client.account_name, params.get("mounts", "storage_mount_container_name")),
                relative_mount_path="{}-{}".format(blob_service_client.account_name, params.get(
                    "mounts", "storage_mount_container_name")),
                mount_options=params.get("mounts", "nfs_mountoptions")
            )
        )
    ]

    if not batch_service_client.pool.exists(pool_id):
        pool = batchmodels.PoolAddParameter(
            id=pool_id,
            virtual_machine_configuration=vm_config,
            vm_size=params.get("vmpool", "vm_size"),
            target_dedicated_nodes=params.get("vmpool", "pool_node_count"),
            enable_inter_node_communication=True,
            start_task=batchmodels.StartTask(
                command_line="/bin/bash -c wget -o https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb \
                                dpkg -i packages-microsoft-prod.deb \
                                apt-get update \
                                wget -o https://raw.githubusercontent.com/Azure/batch-insights/master/scripts/run-linux.sh | bash",
                environment_settings=envs,
                user_identity=batchmodels.UserIdentity(
                    auto_user=batchmodels.AutoUserSpecification(
                        scope=batchmodels.AutoUserScope.pool,
                        elevation_level=batchmodels.ElevationLevel.admin)
                ),
                wait_for_success=True,
                max_task_retry_count=3,
            ),
            mount_configuration=mounts
        )
        batch_service_client.pool.add(pool)


def execute_batchapi(global_cfg: ConfigParser, params_cfg: ConfigParser):
    """Execute the batchapi with the specified Configuration

    Args:
        global_cfg (ConfigParser): the global configuration to use 
        params_cfg (ConfigParser): the specific configurations to use
    """

    batch_account_name = global_cfg.get("batch", "batch_account_name")
    batch_account_key = global_cfg.get("batch", "batch_account_key")
    batch_account_url = global_cfg.get("batch", "batch_account_url")

    storage_account_name = global_cfg.get("storage", "storage_account_name")
    storage_account_key = global_cfg.get("storage", "storage_account_key")
    storage_account_url = global_cfg.get("storage", "storage_blob_url")

    job_name = params_cfg.get("vmpool", "job_id")
    pool_id = params_cfg.get("vmpool", "pool_id")

    env_config = [
        batchmodels.EnvironmentSetting(
            name="AZURE_INSIGHTS_INSTRUMENTATION_KEY",
            value=global_cfg.get(
                "insights", "app_insights_instrumentation_key")
        ),
        batchmodels.EnvironmentSetting(
            name="BATCH_INSIGHTS_DOWNLOAD_GIT_URL",
            value="https://github.com/Azure/batch-insights/releases/download/{}/batch-insights".format(
                global_cfg.get("insights", "batch_git_version"))
        ),
        batchmodels.EnvironmentSetting(
            name="APP_INSIGHTS_APP_ID",
            value=global_cfg.get("insights", "app_insights_app_id")
        )
    ]
    common.helpers.print_configuration(global_cfg)
    common.helpers.print_configuration(params_cfg)

    credentials = batch_auth.SharedKeyCredentials(
        account_name=batch_account_name,
        key=batch_account_key
    )

    batch_client = BatchServiceClient(
        credentials=credentials,
        batch_url=batch_account_url
    )

    blob_client = BlobServiceClient(
        account_url=storage_account_url,
        credential=storage_account_key
    )
    job_id = common.helpers.generate_unique_resource_name(job_name)

    try:
        creat_pool_if_not_exists(
            batch_client, blob_client, pool_id, params_cfg, env_config)
    except Exception as err:
        print(err)


if __name__ == "__main__":

    global_cfg = ConfigParser()
    global_cfg.read(common.helpers.SAMPLE_CONFIG_FILE_NAME)

    params_cfg = ConfigParser()
    params_cfg.read(os.path.splitext(os.path.basename(__file__))[0] + ".cfg")

    execute_batchapi(global_cfg, params_cfg)
