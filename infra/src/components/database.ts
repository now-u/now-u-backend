import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import { BaseStackReference } from "../stacks/base_stack";

export type DatabaseArgs = {
	databaseName: string,
	baseStackOutput: BaseStackReference,
}

export class Database extends pulumi.ComponentResource {
	serverFullyQualifiedDomainName: pulumi.Output<string>
	name: pulumi.Output<string>

	constructor(name: string, args: DatabaseArgs, opts?: pulumi.ComponentResourceOptions) {
		super("infra_shared_components:components:Database", name, {}, opts);

		const database = new azure.dbforpostgresql.Database(
			`${name}-db`,
			{
				databaseName: args.databaseName,
				resourceGroupName: args.baseStackOutput.resourceGroupName.value,
				serverName: args.baseStackOutput.postgresServerName.value,
			}
		)

		this.serverFullyQualifiedDomainName = args.baseStackOutput.postgresServerFullyQualifiedDomainName.value
		this.name = database.name
		this.registerOutputs({});
	}
}
