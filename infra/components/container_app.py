from typing import Optional
from dataclasses import dataclass

import pulumi
from pulumi import Inputs, ResourceOptions
from pulumi_azure_native import app
import pulumi_cloudflare as cloudflare

from components.registry import RegistryWithCredentials

config = pulumi.Config()
current_stack = pulumi.StackReference(
  f"JElgar/{pulumi.get_project()}/{pulumi.get_stack()}"
);

class ContainerAppWithCustomDomain(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        custom_domain: pulumi.Input[str],
        template: pulumi.Input[app.TemplateArgs],
        container_port: Optional[pulumi.Input[int]],
        registry: RegistryWithCredentials,
        environment: app.ManagedEnvironment,
        resource_group_name: Optional[pulumi.Input[str]] = None,
        props: Inputs | None = None,
        opts: ResourceOptions | None = None,
        remote: bool = False
    ) -> None:
        super().__init__('ContainerAppWithCustomDomain', name, props, opts, remote)

        certifacate_id_output_name = f"{custom_domain}-certificate-id"

        txt = cloudflare.Record(
            f"{custom_domain}-dns-verification-txt",
            zone_id=config.require_secret("cloudflareZoneId"),
            type="TXT",
            ttl=60,
            name=f"asuid.{custom_domain}",
            value=environment.custom_domain_configuration.custom_domain_verification_id,
        )

        a = cloudflare.Record(
            f"{custom_domain}-dns-verification-a",
            zone_id=config.require_secret("cloudflareZoneId"),
            type="A",
            ttl=60,
            name=f"{custom_domain}",
            value=environment.static_ip,
        )

        # There is no way to create a certifacte in one go. Instead we have to
        # first create the without relying on the certifacte and then rerun
        # pulumi to update the app to use the certifacte
        certificate_id = current_stack.get_output(certifacate_id_output_name)
        custom_domain_args = app.CustomDomainArgs(
            name=custom_domain,
            binding_type=app.BindingType.DISABLED,
        ) if certificate_id is None else app.CustomDomainArgs(
            name=custom_domain,
            binding_type=app.BindingType.SNI_ENABLED,
            certificate_id=certificate_id
        )

        container_app = app.ContainerApp(
            f"{name}-container-app",
            resource_group_name=resource_group_name,
            environment_id=environment.id,
            configuration=app.ConfigurationArgs(
                ingress=app.IngressArgs(
                    external=True,
                    target_port=container_port,
                    custom_domains=[
                        custom_domain_args
                    ],
                    transport=app.IngressTransportMethod.HTTP,
                ),
                registries=[
                    app.RegistryCredentialsArgs(
                        server=registry.login_server,
                        username=registry.username,
                        password_secret_ref="registry-password",
                    )
                ],
                secrets=[
                    app.SecretArgs(
                       name="registry-password",
                       value=registry.password,
                    )
                ],
            ),
            template=template,
        )

        certificate = app.ManagedCertificate(
            f"{custom_domain}-certificate",
            resource_group_name=resource_group_name,
            environment_name=environment.name,
            managed_certificate_name="causes-service-certificate",
            properties=app.ManagedCertificatePropertiesArgs(
                domain_control_validation=app.ManagedCertificateDomainControlValidation.HTTP,
                subject_name=custom_domain,
            ),
            opts = pulumi.ResourceOptions(depends_on=[txt, a, container_app]),
        )

        self.custom_domain = custom_domain

        pulumi.export(certifacate_id_output_name, certificate.id)
