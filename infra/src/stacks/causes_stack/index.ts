import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import { jsonStringify } from "@pulumi/pulumi";

import { Application, Registry, Database } from "../../components";

import { baseStackFunction, BaseStackOutput } from '../base_stack';

// TODO Ignore this infra dir from docker

export async function causesStackFunction(baseStackOutput: BaseStackOutput): Promise<Record<string, any>> {
	const config = new pulumi.Config()
	
	const baseDomain = "dev.apiv2.now-u.com"
	
	const causesServiceDomain = `api.{base_domain}`
	
	const database = new Database(
		"causes-service-database",
		{
			// TODO Add stack name
			databaseName: "csDb",
			baseStackOutput,
		}
	)
	
	const storageAccount = new azure.storage.StorageAccount(
		"cs-static-files",
		{
			resourceGroupName: baseStackOutput.resourceGroupName,
			kind: azure.storage.Kind.BlobStorage,
			sku: {
				name: azure.storage.SkuName.Standard_LRS,
			},
			accessTier: azure.storage.AccessTier.Hot,
		}
	)
	
	const storageAccountKey = pulumi.all(
		[storageAccount.name, baseStackOutput.resourceGroupName]
	).apply(([accountName, resourceGroupName]) =>
		azure.storage.listStorageAccountKeys({
			accountName,
			resourceGroupName,
		})
	)
	
	const staticFilesStorageContainer = new azure.storage.BlobContainer(
		"cs-static-storage",
		{
			accountName: storageAccount.name,
			resourceGroupName: baseStackOutput.resourceGroupName,
			publicAccess: azure.storage.PublicAccess.Container,
		}
	)
	
	const containerApp = new Application(
		`causes-service-app`,
		{
			env: [
				{
					name: "BASE_URL",
					value: `https://${causesServiceDomain}`,
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
					value: database.fully_qualified_domain_name
				},
			],
			containerPort: 5000,
			template: {
				scale: {
					minReplicas: 1,
				},
				containers: [
					{
						name: "causes-service",
						image: image.imageName,
					}
				]
			}
		}
	);

	return {
		containerAppId: containerApp.id,
	}
}
