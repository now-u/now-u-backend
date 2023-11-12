import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native"
import * as github from "@pulumi/github";
import { StackCreationOutput } from "../../utils/outputType";

// TODO Move name to constants in infra package, so this can be fetched

// TODO Share type nonsense
export type BaseStackReference = StackCreationOutput<Awaited<ReturnType<typeof baseStackFunction>>>

export async function baseStackFunction() {
	const config = new pulumi.Config()

	const resourceGroup = new azure.resources.ResourceGroup(
		"nowu-infra-resource-group"
	)
	
	const workspace = new azure.operationalinsights.Workspace(
		"loganalytics",
		{
			resourceGroupName: resourceGroup.name,
			sku: {
				name: "PerGB2018",
			},
			retentionInDays: 30,
		}
	)
	
	const workspaceSharedKey = pulumi.all([resourceGroup.name, workspace.name]).apply(([resourceGroupName, workspaceName]) => 
		azure.operationalinsights.getSharedKeys({
			resourceGroupName, workspaceName
		})
	)
	
	// TODO Worth looking at... could be simpler than having to implement this networking manually
	// https://www.pulumi.com/registry/packages/azure-native/api-docs/servicelinker/linker/
	const virtualNetwork = new azure.network.VirtualNetwork(
		"nowu-infra-db-virtual-network",
		{
			addressSpace: {
				addressPrefixes: ["10.0.0.0/16"],
			},
			flowTimeoutInMinutes: 10,
			resourceGroupName: resourceGroup.name,
			virtualNetworkName: "nowu-infra-vnet",
		}
	)
	
	const internalDnsZone = new azure.network.PrivateZone(
		"nowu-infra-db-network-dns-zone",
		{
			// TODO Can this be lowercase
			location: "Global",
			resourceGroupName: resourceGroup.name,
			privateZoneName: "nowu.postgres.database.azure.com"
		}
	)
	
	const networkLink = new azure.network.VirtualNetworkLink(
		"nowu-infra-db-network-link",
		{
			location: "global",
			// TODO What is this?
			registrationEnabled: true,
			resourceGroupName: resourceGroup.name,
			privateZoneName: internalDnsZone.name,
			virtualNetwork: {
				id: virtualNetwork.id,
			},
		}
	)
	
	const dbSubnet = new azure.network.Subnet(
		"nowu-infra-db-subnet",
		{
			// TODO Do all these fixed names cause issues if we have multiple accounts? Can I stick stack name in here?
			virtualNetworkName: virtualNetwork.name,
			name: "nowu-infra-db-subnet",
			addressPrefix: "10.0.0.0/24",
			resourceGroupName: resourceGroup.name,
			// TODO Why 2 names?
			subnetName: "nowu-infra-db-subnet",
			delegations: [
				{
					name: "Postgres delegation",
					serviceName: "Microsoft.DBforPostgreSQL/flexibleServers",
				}
			],
		}
	)
	
	const containerAppSubnet = new azure.network.Subnet(
		"nowu-infra-container-app-subnet",
		{
			virtualNetworkName: virtualNetwork.name,
			name: "nowu-infra-container-app-subnet",
			addressPrefix: "10.0.2.0/23",
			resourceGroupName: resourceGroup.name,
			subnetName: "nowu-infra-container-app-subnet",
		}
	)

	const postgresUser = config.requireSecret("databaseUser")
	const postgresPassword = config.requireSecret("databasePassword")
	
	const postgresServer = new azure.dbforpostgresql.Server(
		"nowu-infra-db-server",
		{
			// TODO Move to secrets
			serverName: "nowu-infra-db-server",
			administratorLogin: postgresUser,
			administratorLoginPassword: postgresPassword,
			backup: {
				backupRetentionDays: 7,
			},
			storage: {
				storageSizeGB: 32,
			},
			sku: {
				name: "Standard_B1ms",
				tier: azure.dbforpostgresql.SkuTier.Burstable,
			},
			resourceGroupName: resourceGroup.name,
			version: azure.dbforpostgresql.ServerVersion.ServerVersion_14,
			network: {
				delegatedSubnetResourceId: dbSubnet.id,
				privateDnsZoneArmResourceId: internalDnsZone.id,
			},
		},
		{
			dependsOn: [networkLink],
		}
	)

	const registry = new azure.containerregistry.Registry(
		"nowu-infra-registry",
		{
			registryName: "nowuRegistry",
			resourceGroupName: resourceGroup.name,
			adminUserEnabled: true,
			sku: {
				name: azure.containerregistry.SkuName.Standard,
			},
		}
	)
			
	const managedEnvironment = new azure.app.ManagedEnvironment(
		"nowu-infra-managed-environment",
		{
			resourceGroupName: resourceGroup.name,
			appLogsConfiguration: {
				// TODO Check if I can change the name above and use ref here
				destination: "log-analytics",
				logAnalyticsConfiguration: {
					customerId: workspace.customerId,
					sharedKey: workspaceSharedKey.apply(k => k.primarySharedKey!),
				}
			},
			vnetConfiguration: {
				infrastructureSubnetId: containerAppSubnet.id,
			}
		}
	)
	
	const registryCredentials = pulumi.all([registry.name, resourceGroup.name]).apply(([registryName, resourceGroupName]) => {
		return azure.containerregistry.listRegistryCredentials({
			registryName,
			resourceGroupName,
		})
	});

	new github.ActionsSecret("registryUrlGithubActionSecret", {
		repository: "now-u-backend",
		secretName: "REGISTRY_URL",
		plaintextValue: registry.loginServer,
	});
	new github.ActionsSecret("registryUsernameGithubActionsSecret", {
		repository: "now-u-backend",
		secretName: "REGISTRY_USERNAME",
		plaintextValue: registryCredentials.apply(c => c.username!),
	}); 
	new github.ActionsSecret("registryPasswordGithubActionsSecret", {
		// TODO Share this
		repository: "now-u-backend",
		// TODO Open ticket to pulumi that if secret name is invalid, it explodes
		secretName: "REGISTRY_PASSWORD",
		// TODO Share this
		plaintextValue: registryCredentials.apply(c => c.passwords![0].value!),
	});

	return {
		resourceGroupName: resourceGroup.name,
		postgresServerName: postgresServer.name,
		postgresServerFullyQualifiedDomainName: postgresServer.fullyQualifiedDomainName,
		postgresUser: postgresUser,
		postgresPassword: postgresPassword,
		containerAppEnvironmentId: managedEnvironment.id,
		containerAppEnvironmentName: managedEnvironment.name,
		containerAppEnvironmentStaticIp: managedEnvironment.staticIp,
		// TODO This must be a secret output
		containerAppEnvironmentCustomDomainVerificationId: managedEnvironment.customDomainConfiguration.apply(output => output!.customDomainVerificationId!),
		registryServer: registry.loginServer,
		registryName: registry.name,
		registryUsername: registryCredentials.username!.apply(u => u!),
		// TODO This must be a secret output
		registryPassword: pulumi.secret(registryCredentials.passwords!.apply(p => p![0].value!)),
		// TODO This is not a secret ref
		registryPasswordSecretRef: registryCredentials.passwords!.apply(p => p![0].name!),
	}
}
