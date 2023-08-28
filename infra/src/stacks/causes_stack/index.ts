import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";

import { Application, Database } from "../../components";

import { BaseStackReference } from '../base_stack';
import { BASE_DOMAIN, CAUSES_SERVICE_IMAGE_TAG_INPUT_NAME } from "../../utils/constants";
import { JitRequest } from "@pulumi/azure-native/solutions/jitRequest";

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

    const containerAppIdOutputName = "causes-container-app-id" as const;
	const containerAppIdOutputValue = currentStack.getOutput(containerAppIdOutputName) as pulumi.Output<string>;

	const domainPrefix = "causes"

	const app = new Application(
		`causes-service-app`,
		{
			baseStackOutput,
			domainPrefix,
			containerPort: 5000,
			imageName: "now-u-causes",
			imageTag: config.require(CAUSES_SERVICE_IMAGE_TAG_INPUT_NAME),
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
					value: database.name,
				},
				// TODO Fix
				{
					name: "DATABASE_USER",
					value: "superduperadmin",
				},
				{
					name: "DATABASE_PASSWORD",
					value: "superduperadmin",
				},
				{
					name: "DATABASE_HOST",
					value: database.serverFullyQualifiedDomainName,
				},
				{
					name: "DATABASE_PORT",
					value: "5432",
				},
				{
					name: "DJANGO_SUPERUSER_EMAIL",
                    value: config.requireSecret("djangoAdminEmail"),
				},
				{
					name: "DJANGO_SUPERUSER_PASSWORD",
                    value: config.requireSecret("djangoAdminPassword"),
				},
				{
					name: "MAILCHIMP_API_KEY",
                    value: config.requireSecret("mailchimpApiKey"),
				},
				{
					name: "MAILCHIMP_LIST_ID",
                    value: config.requireSecret("mailchimpListId"),
				},
				// TODO Set these config things
				{
					name: "MAILCHIMP_SERVER",
                    value: config.require("mailchimpServer"),
				},
			],
			containerAppIdOutputValue,
		}
	);

	// TODO Create shared component for this so you only have to give name of resource
	// Will hvae to generate base64 content and replace registry name in there
	new azure.containerregistry.Task('purge-cs-containers-task', {
		registryName: baseStackOutput.registryName.value,
		resourceGroupName: baseStackOutput.resourceGroupName.value,
		status: 'Enabled',
		step: {
			type: 'EncodedTask',
			encodedTaskContent: 'dmVyc2lvbjogdjEuMS4wCnN0ZXBzOiAKICAtIGNtZDogYWNyIHB1cmdlIC0tZmlsdGVyICdub3ctdS1jYXVzZXM6LionICAtLWFnbyA3ZCAtLWtlZXAgNQogICAgZGlzYWJsZVdvcmtpbmdEaXJlY3RvcnlPdmVycmlkZTogdHJ1ZQogICAgdGltZW91dDogMzYwMAo='
		},
		trigger: {
			timerTriggers: [
				{
					name: 'Daily cs purge',
					schedule: '0 0 * * *',
				}
			]
		},
		platform: {
			architecture: 'amd64',
			os: 'Linux',
		}
	});

	return {
		[containerAppIdOutputName]: app.containerAppId,
	}
}
