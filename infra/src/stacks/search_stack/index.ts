import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import { Application } from "../../components";
import { StackCreationOutput } from "../../utils/outputType";
import { getCurrentStack } from "../../utils/stack";
import { BaseStackReference } from "../base_stack";

export type SearchStackReference = StackCreationOutput<Awaited<ReturnType<typeof searchStackFunction>>>

export async function searchStackFunction(baseStackOutput: BaseStackReference) {
	const config = new pulumi.Config()
	const containerAppIdOutputName = "search-container-app-id" as const;
	
	const currentStack = getCurrentStack();
	const containerAppIdOutputValue = currentStack.getOutput(containerAppIdOutputName) as pulumi.Output<string>;
	
	const domainPrefix = "search"

	const masterKey = config.requireSecret('meiliMasterKey')
	
	// TODO Share one storage account or create shared construct to create one
	const storageAccount = new azure.storage.StorageAccount(
		"searchstatic",
		{
			resourceGroupName: baseStackOutput.resourceGroupName.value,
			kind: azure.storage.Kind.StorageV2,
			sku: {
				name: azure.storage.SkuName.Standard_LRS,
			},
			accessTier: azure.storage.AccessTier.Hot,
		}
	)

	const fileShare = new azure.storage.FileShare(
		"searchMeilidataFileShare",
		{
			accountName: storageAccount.name,
			resourceGroupName: baseStackOutput.resourceGroupName.value,
			enabledProtocols: azure.types.enums.storage.EnabledProtocols.SMB,
			shareQuota: 1024,
			shareName: 'meilisearch-fileshare',
		}
	)

	const storageAccountKey = pulumi.all(
		[storageAccount.name, baseStackOutput.resourceGroupName.value]
	).apply(([accountName, resourceGroupName]) =>
		azure.storage.listStorageAccountKeys({
			accountName,
			resourceGroupName,
		})
	).apply(({keys}) => keys[0].value!)

	const managedEnvironmentsStorage = new azure.app.ManagedEnvironmentsStorage("searchAppStorage", {
		environmentName: baseStackOutput.containerAppEnvironmentName.value,
		storageName: "search-app-storage",
    	properties: {
    	    azureFile: {
    	        accessMode: azure.types.enums.app.AccessMode.ReadWrite,
    	        accountKey: storageAccountKey,
    	        accountName: storageAccount.name,
    	        shareName: fileShare.name,
    	    },
    	},
    	resourceGroupName: baseStackOutput.resourceGroupName.value,
	});
	

	const app = new Application(
		`search-service-app`,
		{
			baseStackOutput,
			domainPrefix,
			containerPort: 7700,
			imageName: 'meilisearch',
			imageTag: 'getmeili/meilisearch:v1.3.4',
			containerAppIdOutputValue,
			env: [
				{
					name: 'MEILI_MASTER_KEY',
					value: masterKey,
				}
			],
			volumes: [
				{
					name: 'meili-data',
					storageType: azure.types.enums.app.StorageType.AzureFile,
					storageName: managedEnvironmentsStorage.name,
				}
			],
			volumeMounts: [
				{
					volumeName: 'meili-data',
					mountPath: '/meili_data',
				}
			],
			// For now meilisearch doesn't support distributed deployments
			// https://github.com/meilisearch/meilisearch/discussions/1095
			// For now if multiple replicas are allowed only one replica 
			// will be updated when pushing to the index
			maxReplicas: 1,
		}
	);
	
	return {
		[containerAppIdOutputName]: app.containerAppId,
		url: `https://${app.domain}`,
		masterKey,
	}
}
