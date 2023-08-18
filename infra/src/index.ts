import { InlineProgramArgs, LocalWorkspace } from "@pulumi/pulumi/automation";
import * as pulumi from "@pulumi/pulumi";

import path from "path";
import { baseStackFunction } from './stacks/base_stack';
import { BASE_STACK_PROJECT_NAME } from "./utils/constants";

async function deploy() {
	const args: InlineProgramArgs = {
        stackName: "dev",
        projectName: BASE_STACK_PROJECT_NAME,
        program: baseStackFunction,
    };
	const stack = await LocalWorkspace.createOrSelectStack(args, { workDir: path.dirname(__dirname) + '/src/stacks/base_stack'});

	stack.workspace.installPlugin("azure-native", "2.3.0");
	stack.workspace.selectStack("dev")

	const upRes = await stack.up({ onOutput: console.info, color: "always" });

	// TODO Support desotry

	console.log(`update summary: \n${JSON.stringify(upRes.summary.resourceChanges, null, 4)}`);
	console.log('Outputs: ', upRes.outputs);
}

deploy().catch((err) => console.error(err));
