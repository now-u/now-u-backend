import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import * as cloudflare from "@pulumi/cloudflare";
import * as docker from "@pulumi/docker";

import { BindingType, ManagedCertificateDomainControlValidation } from "@pulumi/azure-native/app";
import { BaseStackReference } from "../stacks/base_stack";
import { BASE_DOMAIN } from "../utils/constants";

export type ApplicationArgs = {
	env: pulumi.Input<pulumi.Input<azure.types.input.app.EnvironmentVarArgs>[]>,
	// TODO Merge
	volumes?: pulumi.Input<pulumi.Input<azure.types.input.app.VolumeArgs>[]>,
	volumeMounts?: pulumi.Input<pulumi.Input<azure.types.input.app.VolumeMountArgs>[]>,
	containerPort: number,
	domainPrefix: string | undefined,
	imageName: string,
	imageTag: string,

	containerAppIdOutputValue: pulumi.Output<string>,
	baseStackOutput: BaseStackReference,

	minReplicas?: number,
	maxReplicas?: number,
};

export class Application extends pulumi.ComponentResource {
	containerAppId: pulumi.Output<string>
	domain: string

	constructor(name: string, args: ApplicationArgs, opts?: pulumi.ComponentResourceOptions) {
		super("infra_shared_components:components:Application", name, {}, opts);

		const config = new pulumi.Config()

		const resourceGroupName = args.baseStackOutput.resourceGroupName;

		const domain = args.domainPrefix ? `${args.domainPrefix}.${BASE_DOMAIN}`: undefined

		let txtRecord: cloudflare.Record | undefined;
		let aRecord: cloudflare.Record | undefined;

		if (domain !== undefined) {
			txtRecord = new cloudflare.Record(
				`${args.domainPrefix}-dns-verification-txt`,
				{
					// TODO Can we use cloudlfare:zoneId?
					zoneId: config.requireSecret("cloudflareZoneId"),
					name: `asuid.${domain}`,
					value: args.baseStackOutput.containerAppEnvironmentCustomDomainVerificationId.value,
					type: "TXT",
					ttl: 60,
				}
			)

			aRecord = new cloudflare.Record(
				`${args.domainPrefix}-dns-verification-a`,
				{
					zoneId: config.requireSecret("cloudflareZoneId"),
					name: domain,
					value: args.baseStackOutput.containerAppEnvironmentStaticIp.value,
					type: "A",
					ttl: 60,
				}
			)
		}

		// There is no way to create a certifacte in one go. Instead we have to
		// first create the without relying on the certifacte and then rerun
		// TODO I assume this will never be none should we apply here
		this.containerAppId = args.containerAppIdOutputValue.apply(id => {
			// pulumi to update the app to use the certifacte
			let certificate: azure.app.ManagedCertificate | undefined = undefined;
			if (id !== undefined && args.domainPrefix !== undefined) {
				certificate = new azure.app.ManagedCertificate(
					`${args.domainPrefix}-certificate`,
					{
						resourceGroupName: resourceGroupName.value,
						environmentName: args.baseStackOutput.containerAppEnvironmentName.value,
						managedCertificateName: `${args.domainPrefix}-certificate`,
						properties: {
							domainControlValidation: ManagedCertificateDomainControlValidation.HTTP,
							subjectName: domain,
						}
					},
					{ dependsOn: txtRecord && aRecord && [txtRecord, aRecord] },
				)
			}

			const containerApp = new azure.app.ContainerApp(
				`${name}-app`,
				{
					template: {
						scale: {
							minReplicas: args.minReplicas ?? 1,
							maxReplicas: args.maxReplicas,
						},
						volumes: args.volumes,
						containers: [
							{
								name: args.imageName,
								image: args.imageTag,
								// TODO Take as arg
								resources: {
									cpu: 1,
									memory: "2Gi",
								},
								env: args.env,
								volumeMounts: args.volumeMounts,
							},
						]
					},
					environmentId: args.baseStackOutput.containerAppEnvironmentId.value,
					resourceGroupName: resourceGroupName.value,
					configuration: {
						ingress: {
							external: true,
							targetPort: args.containerPort,
							customDomains: domain !== undefined ? [
								{
									name: domain,
									certificateId: certificate?.id,
									bindingType: certificate !== undefined ? BindingType.SniEnabled : BindingType.Disabled,
								}
							] : undefined
						},
						secrets: [
							{
								// TODO COnstant
								name: "registry-password",
								// TODO Remove seret ref
								value: args.baseStackOutput.registryPassword.value,

							}
						],
						registries: [
							{
								server: args.baseStackOutput.registryServer.value,
								username: args.baseStackOutput.registryUsername.value,
								passwordSecretRef: "registry-password",
							},
						]
					},
				},
				{ dependsOn: certificate !== undefined ? [certificate] : txtRecord && aRecord && [txtRecord, aRecord] },
			)
		
			return containerApp.id
		})
			
		this.domain = domain ?? "TODO - containerApp.something"

		// TODO For now we are passing in the image tag for the image
		// Not sure if thats the best way, if not we can go back to creating
		// images like this:
		//
		// const dockerImage = new docker.Image(
		// 	`${args.domainPrefix}-image`,
		// 	{
		// 		imageName: args.imageName,
		// 		build: {
		// 			context: args.appPath,
		// 			platform: "linux/amd64",
		// 		},
		// 		registry: {
		// 			server: args.baseStackOutput.registryServer.value,
		// 			username: args.baseStackOutput.registryUsername.value,
		// 			password: args.baseStackOutput.registryPassword.value,
		// 		}
		// 	}
		// )
	}
}
