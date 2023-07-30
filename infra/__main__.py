import pulumi
import pulumi_docker as docker
from pulumi_azure_native import resources, app, operationalinsights, storage, dbforpostgresql, network
import pulumi_cloudflare as cloudflare
from components.container_app import ContainerAppWithCustomDomain

from components.registry import RegistryWithCredentials

# Import the program's configuration settings.
config = pulumi.Config()
causes_service_path = "../causes_service"
image_name = "nowu-causes-service"
image_tag = config.get("imageTag", "0.0.5")
container_port = config.get_int("containerPort", 5000)
cpu = config.get_int("cpu", 1)
memory = config.get_int("memory", 2)

api_host = "dev.apiv2.now-u.com"

# Create a resource group for the container registry.
resource_group = resources.ResourceGroup("resource-group")

workspace = operationalinsights.Workspace("loganalytics",
    resource_group_name=resource_group.name,
    sku=operationalinsights.WorkspaceSkuArgs(name="PerGB2018"),
    retention_in_days=30,
)

workspace_shared_keys = pulumi.Output.all(resource_group.name, workspace.name) \
    .apply(lambda args: operationalinsights.get_shared_keys(
        resource_group_name=args[0],
        workspace_name=args[1],
    ),
)

virtual_network = network.VirtualNetwork(
    "cs-db-network",
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    flow_timeout_in_minutes=10,
    resource_group_name=resource_group.name,
    virtual_network_name="causes-service-vnet",
)

# TODO DO I Need this?
internal_dns_zone = network.PrivateZone(
    "csPrivateZone",
    location="Global",
    private_zone_name="cs.postgres.database.azure.com",
    resource_group_name=resource_group.name,
)

network_link = network.VirtualNetworkLink(
    "cs-db-network-link",
    location="global",
    registration_enabled=True,
    resource_group_name=resource_group.name,
    private_zone_name=internal_dns_zone.name,
    virtual_network=network.SubResourceArgs(
        id = virtual_network.id,
    )
)

db_subnet = network.Subnet(
    "cs-db-network-db-subnet",
    name="causes-db-subnet",
    address_prefix="10.0.0.0/24",
    resource_group_name=resource_group.name,
    subnet_name="causes-db-subnet",
    virtual_network_name=virtual_network.name,
    delegations=[network.DelegationArgs(
        name="Postgres delegation",
        service_name="Microsoft.DBforPostgreSQL/flexibleServers"
    )]
)

container_app_subnet = network.Subnet(
    "cs-db-network-container-app-subnet",
    name="causes-app-subnet",
    address_prefix="10.0.2.0/23",
    resource_group_name=resource_group.name,
    subnet_name="causes-app-subnet",
    virtual_network_name=virtual_network.name,
)

database_server = dbforpostgresql.Server(
    "cs-db-server",
    administrator_login="superduperadmin",
    administrator_login_password="superduperadmin",
    backup=dbforpostgresql.BackupArgs(
        backup_retention_days=7,
    ),
    storage=dbforpostgresql.StorageArgs(
        storage_size_gb=32,
    ),
    sku=dbforpostgresql.SkuArgs(
        name="Standard_B1ms",
        tier=dbforpostgresql.SkuTier.BURSTABLE,
    ),
    server_name="causes-db",
    resource_group_name=resource_group.name,
    version=dbforpostgresql.ServerVersion.SERVER_VERSION_14,
    network=dbforpostgresql.NetworkArgs(
        delegated_subnet_resource_id=db_subnet.id,
        private_dns_zone_arm_resource_id=internal_dns_zone.id,
    ),
    opts=pulumi.ResourceOptions(depends_on=[network_link]),
)

database = dbforpostgresql.Database(
    "cs-db",
    args=dbforpostgresql.DatabaseArgs(
        resource_group_name=resource_group.name,
        server_name=database_server.name,
    )
)

storage_account = storage.StorageAccount(
    "csaccount",
    args=storage.StorageAccountArgs(
        resource_group_name=resource_group.name,
        kind=storage.Kind.BLOB_STORAGE,
        sku=storage.SkuArgs(
            # TODO What is this?
            # https://learn.microsoft.com/en-us/rest/api/storagerp/srp_sku_types
            name=storage.SkuName.STANDARD_LRS,
        ),
        access_tier=storage.AccessTier.HOT,
    )
)

storage_account_key = storage_account.name.apply(
    lambda name: storage.list_storage_account_keys(
        account_name=name,
        resource_group_name=resource_group.name,
    ).keys[0].value
)

causes_service_static_files_storage_container = storage.BlobContainer(
    "cs-static-storage",
    args=storage.BlobContainerArgs(
        account_name=storage_account.name,
        resource_group_name=resource_group.name,
        public_access=storage.PublicAccess.CONTAINER,
    ),
)

registry = RegistryWithCredentials(
    "csRegistry",
    resource_group_name=resource_group.name,
)

managed_env = app.ManagedEnvironment(
    "cs-container-app-env",
    resource_group_name=resource_group.name,
    app_logs_configuration=app.AppLogsConfigurationArgs(
        destination="log-analytics",
        log_analytics_configuration=app.LogAnalyticsConfigurationArgs(
           customer_id=workspace.customer_id,
           shared_key=workspace_shared_keys.apply(lambda r: r.primary_shared_key),
        )
    ),
    vnet_configuration=app.VnetConfigurationArgs(
        infrastructure_subnet_id=container_app_subnet.id,
    ),
)

# Create a container image for the service.
image = docker.Image(
    "cs-image",
    image_name=pulumi.Output.concat(registry.login_server, f"/{image_name}:{image_tag}"),
    build=docker.DockerBuildArgs(
        context=causes_service_path,
        platform="linux/amd64",
    ),
    registry=docker.RegistryArgs(
        server=registry.login_server,
        username=registry.username,
        password=registry.password,
    ),
)

api_url = f"api.{api_host}"
container_app = ContainerAppWithCustomDomain(
    "cs-cawd",
    resource_group_name=resource_group.name,
    environment=managed_env,
    custom_domain=api_url,
    registry=registry,
    container_port=container_port,
    template=app.TemplateArgs(
        containers=[
            app.ContainerArgs(
                name = "causes-service",
                image = image.image_name,
                env=[
                    app.EnvironmentVarArgs(
                        name="BASE_URL",
                        value=api_url,
                    ),
                    app.EnvironmentVarArgs(
                        name="JWT_SECRET",
                        value=config.require_secret("authServiceJwtSecret"),
                    ),
                    app.EnvironmentVarArgs(
                        name="STATIC_FILES_STORAGE_CONTAINER",
                        value=causes_service_static_files_storage_container.name,
                    ),
                    app.EnvironmentVarArgs(
                        name="STATIC_FILES_STORAGE_ACCOUNT_NAME",
                        value=storage_account.name
                    ),
                    app.EnvironmentVarArgs(
                        name="STATIC_FILES_STORAGE_ACCOUNT_KEY",
                        value=storage_account_key,
                    ),
                    app.EnvironmentVarArgs(
                        name="DATABASE_NAME",
                        value=database.name,
                    ),
                    app.EnvironmentVarArgs(
                        name="DATABASE_USER",
                        value="superduperadmin",
                    ),
                    app.EnvironmentVarArgs(
                        name="DATABASE_PASSWORD",
                        value="superduperadmin",
                    ),
                    app.EnvironmentVarArgs(
                        name="DATABASE_HOST",
                        value=database_server.fully_qualified_domain_name,
                    ),
                    app.EnvironmentVarArgs(
                        name="DATABASE_PORT",
                        value="5432",
                    ),
                    app.EnvironmentVarArgs(
                        name="DJANGO_SUPERUSER_PASSWORD",
                        value=config.require_secret("djangoAdminPassword"),
                    ),
                    app.EnvironmentVarArgs(
                        name="DJANGO_SUPERUSER_EMAIL",
                        value=config.require_secret("djangoAdminEmail"),
                    )
                ],
            ),
        ]
    )
)


pulumi.export("url", container_app.custom_domain)
pulumi.export("ip", managed_env.static_ip)
