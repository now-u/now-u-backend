import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";

import { Application, Database } from "../../components";

import { BaseStackReference } from '../base_stack';
import { BASE_DOMAIN } from "../../utils/constants";

export async function causesStackFunction(baseStackOutput: BaseStackReference): Promise<Record<string, any>> {
	const config = new pulumi.Config()
	
	const database = new Database(
		"causes-service-database",
		{
			// TODO Add stack name
			databaseName: "csDb",
			baseStackOutput,
		}
	)
	
	const storageAccount = new azure.storage.StorageAccount(
		"csstatic",
		{
			resourceGroupName: baseStackOutput.resourceGroupName.value,
			kind: azure.storage.Kind.BlobStorage,
			sku: {
				name: azure.storage.SkuName.Standard_LRS,
			},
			accessTier: azure.storage.AccessTier.Hot,
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
	
	const staticFilesStorageContainer = new azure.storage.BlobContainer(
		"cs-static-storage",
		{
			accountName: storageAccount.name,
			resourceGroupName: baseStackOutput.resourceGroupName.value,
			publicAccess: azure.storage.PublicAccess.Container,
		}
	)
	
	const currentStack = new pulumi.StackReference(
		`${pulumi.getOrganization()}/${pulumi.getProject()}/${pulumi.getStack()}`
	)

    const containerAppIdOutputName = "causes-container-app-id" as const
	let containerAppIdOutputValue = currentStack.getOutput(containerAppIdOutputName) as pulumi.Output<string>

	const domainPrefix = "causes"
	const containerApp = new Application(
		`causes-service-app`,
		{
			baseStackOutput,
			domainPrefix,
			containerPort: 5000,
			imageName: "causes-service",
			appPath: "../../../../causes_service",
			env: [
				{
					name: "BASE_URL",
					// TODO Shouldn't have to regenerate this
					value: `https://${domainPrefix}.${BASE_DOMAIN}`,
				},
				{
					name: "JWT_SECRET",
					value: config.requireSecret("authServiceJwtSecret"),
				},
				{
					name: "STATIC_FILES_STORAGE_CONTAINER",
					value: staticFilesStorageContainer.name,
				},
				{
					name: "STATIC_FILES_STORAGE_ACCOUNT_NAME",
					value: storageAccount.name,
				},
				{
					name: "STATIC_FILES_STORAGE_ACCOUNT_KEY",
					value: storageAccountKey,
				},
				{
					name: "DATABASE_NAME",
					value: "superduperadmin",
				},
				{
					name: "DATABASE_PASSWORD",
					value: "superduperadmin",
				},
				{
					name: "DATABASE_HOST",
					value: database.serverName,
				},
			],
			containerAppIdOutputValue,
		}
	);

	return {
		[containerAppIdOutputName]: containerAppIdOutputValue,
	}
}
