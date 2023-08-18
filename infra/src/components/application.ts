import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import * as cloudflare from "@pulumi/cloudflare";
import * as docker from "@pulumi/docker";

import { BindingType, ManagedCertificateDomainControlValidation } from "@pulumi/azure-native/app";
import { BaseStackOutput } from "../stacks/base_stack";

export type ApplicationArgs = {
	env: pulumi.Input<pulumi.Input<azure.types.input.app.EnvironmentVarArgs>[]>,
	containerPort: number,
	customDomain: string,
	imageName: string,
	appPath: string,
	baseStackOutput: BaseStackOutput, 
};

export class Application extends pulumi.ComponentResource {
	constructor(name: string, args: ApplicationArgs, opts?: pulumi.ComponentResourceOptions) {
		super("infra_shared_components:components:Application", name, {}, opts);

		const resourceGroupName = args.baseStackOutput.resourceGroupName;

		const config = new pulumi.Config()
		const currentStack = new pulumi.StackReference(
			`JElgar/${pulumi.getProject()}/${pulumi.getStack()}`
		)
        const containerAppIdOutputName = `${args.customDomain}-container-app-id`

		const txtRecord = new cloudflare.Record(
			`${args.customDomain}-dns-verification-txt`,
			{
				zoneId: config.requireSecret("cloudflareZoneId"),
				name: `asuid.${args.customDomain}`,
				value: args.baseStackOutput.containerAppEnvironmentCustomDomainVerificationId,
				type: "TXT",
				ttl: 60,
			}
		)

		const aRecord = new cloudflare.Record(
			`${args.customDomain}-dns-verification-a`,
			{
				zoneId: config.requireSecret("cloudflareZoneId"),
				name: args.customDomain,
				value: args.baseStackOutput.containerAppEnvironmentStaticIp,
				type: "A",
				ttl: 60,
			}
		)

		// There is no way to create a certifacte in one go. Instead we have to
		// first create the without relying on the certifacte and then rerun
		// pulumi to update the app to use the certifacte
		const containerAppId = currentStack.getOutput(containerAppIdOutputName)

		let certificate: azure.app.ManagedCertificate | undefined = undefined;
		// TODO I assume this will never be none should we apply here
		if (containerAppId !== undefined) {
			certificate = new azure.app.ManagedCertificate(
				`${args.customDomain}-certificate`,
				{
					resourceGroupName: resourceGroupName,
					environmentName: args.baseStackOutput.containerAppEnvironmentName,
					managedCertificateName: `${args.customDomain}-certificate`,
					properties: {
						domainControlValidation: ManagedCertificateDomainControlValidation.TXT,
						subjectName: args.customDomain,
					}
				},
				{ dependsOn: [txtRecord, aRecord] },
			)
		}

		const dockerImage = new docker.Image(
			`${args.customDomain}-image`,
			{
				imageName: args.imageName,
				build: {
					context: args.appPath,
					platform: "linux/amd64",
				},
				registry: {
					server: args.baseStackOutput.registryServer,
					username: args.baseStackOutput.registryUsername,
					password: args.baseStackOutput.registryPassword,
				}
			}
		)

		const containerApp = new azure.app.ContainerApp(
			`${name}-container_app`,
			{
				template: {
					scale: {
						minReplicas: 1,
					},
					containers: [
						{
							name: args.imageName,
							image: dockerImage.imageName,
							// TODO Take as arg
							resources: {
								cpu: 1,
								memory: "2Gi",
							},
							env: args.env,
						},
					]
				},
				environmentId: args.baseStackOutput.containerAppEnvironmentId,
				resourceGroupName,
				configuration: {
					ingress: {
						external: true,
						targetPort: args.containerPort,
						customDomains: [
							{
								name: args.customDomain,
								certificateId: certificate?.id,
								bindingType: certificate !== undefined ? BindingType.SniEnabled : BindingType.Disabled,
							}
						]
					},
					registries: [
						{
							server: args.baseStackOutput.registryServer,
							username: args.baseStackOutput.registryUsername,
							passwordSecretRef: args.baseStackOutput.registryPasswordSecretRef,
						},
					]
				},
			},
			{ dependsOn: certificate !== undefined ? [certificate] : [] },
		)

		// TODO I assume this doesn't work
		 this.registerOutputs({
			 [containerAppIdOutputName]: containerApp.id
		})
	}
}
