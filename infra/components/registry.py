import pulumi
from pulumi import Inputs, ResourceOptions
from pulumi_azure_native import containerregistry

class RegistryWithCredentials(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        resource_group_name: pulumi.Input[str],
        props: Inputs | None = None,
        opts: ResourceOptions | None = None,
        remote: bool = False
    ) -> None:
        super().__init__('RegistryWithCredentials', name, props, opts, remote)

        # Create a container registry.
        self.registry = containerregistry.Registry(
            f"{name}Registry",
            containerregistry.RegistryArgs(
                resource_group_name=resource_group_name,
                admin_user_enabled=True,
                sku=containerregistry.SkuArgs(
                    name=containerregistry.SkuName.BASIC,
                ),
            ),
        )

        # Fetch login credentials for the registry.
        self.credentials = containerregistry.list_registry_credentials_output(
            resource_group_name=resource_group_name,
            registry_name=self.registry.name,
        )

        self.login_server = self.registry.login_server

    @property
    def username(self):
        return self.credentials.apply(lambda creds: creds.username)

    @property
    def password(self):
        return self.credentials.apply(lambda creds: creds.passwords[0].value)
