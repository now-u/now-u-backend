import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";

// TODO Remove/Use this component
type RegistryArgs = {
	resourceGroupName: string;
}

export class Registry extends pulumi.ComponentResource {
	private resourceGroupName: string;
	registry: azure.containerregistry.Registry

	constructor(name: string, args: RegistryArgs, opts?: pulumi.ComponentResourceOptions) {
		super("infra_shared_components:components:Registry", name, {}, opts);

		this.registry = new azure.containerregistry.Registry(
			`${name}Registry`,
			{
				resourceGroupName: args.resourceGroupName,
				adminUserEnabled: true,
				sku: {
					name: azure.containerregistry.SkuName.Basic,
				}
			}
		);

		this.resourceGroupName = args.resourceGroupName;

		this.registerOutputs({});
	}

	async getCredentials(): Promise<{ username: pulumi.Output<string>, password: pulumi.Output<string>}> {
		const creds = this.registry.name.apply((registryName) => {
			return azure.containerregistry.listRegistryCredentials({
				registryName,
				resourceGroupName: this.resourceGroupName,
			})
		})

		return {
			username: creds.username!.apply(u => u!),
			password: creds.passwords!.apply(p => p![0].value!),
		}
	}
}
