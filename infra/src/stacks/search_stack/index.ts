import * as pulumi from "@pulumi/pulumi";
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
	const app = new Application(
		`search-service-app`,
		{
			baseStackOutput,
			domainPrefix,
			containerPort: 7700,
			imageName: 'meilisearch',
			imageTag: 'getmeili/meilisearch',
			containerAppIdOutputValue,
			env: [
				{
					name: 'MEILI_MASTER_KEY',
					value: masterKey,
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
