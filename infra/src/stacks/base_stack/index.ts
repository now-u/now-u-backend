import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native"
import { StackCreationOutput } from "../../utils/outputType";

// TODO Move name to constants in infra package, so this can be fetched

// TODO Share type nonsense
export type BaseStackReference = StackCreationOutput<Awaited<ReturnType<typeof baseStackFunction>>>

export async function baseStackFunction() {
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
			location: "global",
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
	
	const postgresServer = new azure.dbforpostgresql.Server(
		"nowu-infra-db-server",
		{
			// TODO Move to secrets
			serverName: "nowu-infra-db-server",
			administratorLogin: "superduperadmin",
			administratorLoginPassword: "superduperadmin",
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

	return {
		resourceGroupName: resourceGroup.name,
		postgresServerName: postgresServer.name,
		containerAppEnvironmentId: managedEnvironment.id,
		containerAppEnvironmentName: managedEnvironment.name,
		containerAppEnvironmentStaticIp: managedEnvironment.staticIp,
		containerAppEnvironmentCustomDomainVerificationId: managedEnvironment.customDomainConfiguration.apply(output => output!.customDomainVerificationId!),
		registryServer: registry.loginServer,
		registryUsername: registryCredentials.username!.apply(u => u!),
		registryPassword: registryCredentials.passwords!.apply(p => p![0].value!),
		registryPasswordSecretRef: registryCredentials.passwords!.apply(p => p![0].name!),
	}
}
