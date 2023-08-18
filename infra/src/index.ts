import { InlineProgramArgs, LocalWorkspace } from "@pulumi/pulumi/automation";
import { command, run, string, boolean, positional, option, flag } from 'cmd-ts';

import path from "path";
import { baseStackFunction, BaseStackReference } from './stacks/base_stack';
import { BASE_STACK_PROJECT_NAME, CAUSES_STACK_PROJECT_NAME } from "./utils/constants";
import { causesStackFunction } from "./stacks/causes_stack";

async function deploy(baseOnly: boolean) {
	const baseStackArgs: InlineProgramArgs = {
        stackName: "dev",
        projectName: BASE_STACK_PROJECT_NAME,
        program: baseStackFunction,
    };
	const baseStack = await LocalWorkspace.createOrSelectStack(baseStackArgs, { workDir: path.dirname(__dirname) + '/src/stacks/base_stack'});

	baseStack.workspace.installPlugin("azure-native", "2.3.0");

	const baseStackUpResult = await baseStack.up({ onOutput: console.info, color: "always" });

	console.log(`Base stack summary: \n${JSON.stringify(baseStackUpResult.summary.resourceChanges, null, 4)}`);

	if (baseOnly) {
		return
	}

	const causesStackArgs: InlineProgramArgs = {
        stackName: "dev",
        projectName: CAUSES_STACK_PROJECT_NAME,
        program: () => causesStackFunction(baseStackUpResult.outputs as BaseStackReference),
	}

	const causesStack = await LocalWorkspace.createOrSelectStack(causesStackArgs, { workDir: path.dirname(__dirname) + '/src/stacks/causes_stack'});

	causesStack.workspace.installPlugin("azure-native", "2.3.0");
	causesStack.workspace.installPlugin("cloudflare", "5.8.0");
	causesStack.workspace.installPlugin("docker", "4.3.1");

	const causesStackUpResult = await causesStack.up({ onOutput: console.info, color: "always" });

	console.log(`Causes stack summary: \n${JSON.stringify(causesStackUpResult.summary.resourceChanges, null, 4)}`);
	
	// TODO Support desotry
}

const cmd = command({
  name: 'deploy',
  description: 'Deploy all infra',
  version: '0.0.1',
  args: {
	  baseOnly: flag({
		type: boolean,
		long: 'base-only',
		short: 'b',
	  })
  },
  handler: async (args) => {
	try {
		await deploy(args.baseOnly)
	} catch(err) {
		console.error(err)
	}
  },
});

run(cmd, process.argv.slice(2));
