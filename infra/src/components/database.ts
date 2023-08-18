import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import { BaseStackOutput } from "../stacks/base_stack";

export type DatabaseArgs = {
	databaseName: string,
	baseStackOutput: BaseStackOutput,
}

export class Database extends pulumi.ComponentResource {
	constructor(name: string, args: DatabaseArgs, opts?: pulumi.ComponentResourceOptions) {
		super("infra_shared_components:components:Database", name, {}, opts);

		new azure.dbforpostgresql.Database(
			`${name}-db`,
			{
				databaseName: args.databaseName,
				resourceGroupName: args.baseStackOutput.resourceGroupName,
				serverName: args.baseStackOutput.postgresServerName,
			}
		)

		this.registerOutputs({});
	}
}
