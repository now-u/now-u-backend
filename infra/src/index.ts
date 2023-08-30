#!/usr/bin/env node
import { InlineProgramArgs, LocalWorkspace } from "@pulumi/pulumi/automation";
import { command, run, boolean, positional, string, flag, subcommands, optional, option } from 'cmd-ts';

import path from "path";
import { baseStackFunction, BaseStackReference } from './stacks/base_stack';
import { BASE_STACK_PROJECT_NAME, CAUSES_SERVICE_IMAGE_TAG_INPUT_NAME, CAUSES_STACK_PROJECT_NAME, SEARCH_STACK_PROJECT_NAME } from "./utils/constants";
import { causesStackFunction } from "./stacks/causes_stack";
import { searchStackFunction, SearchStackReference } from "./stacks/search_stack";

async function createBaseStack() {
	const baseStackArgs: InlineProgramArgs = {
        stackName: "dev",
        projectName: BASE_STACK_PROJECT_NAME,
        program: baseStackFunction,
    };
	const baseStack = await LocalWorkspace.createOrSelectStack(baseStackArgs, { workDir: path.dirname(__dirname) + '/src/stacks/base_stack'});

	baseStack.workspace.installPlugin("azure-native", "2.3.0");
	baseStack.workspace.installPlugin("github", "5.16.0");

	return baseStack;
}

async function createCausesStack(baseStackOutputs: BaseStackReference, searchStackOutputs: SearchStackReference, imageTag: string) {
	const causesStackArgs: InlineProgramArgs = {
        stackName: "dev",
        projectName: CAUSES_STACK_PROJECT_NAME,
        program: () => causesStackFunction(baseStackOutputs, searchStackOutputs),
	}

	const causesStack = await LocalWorkspace.createOrSelectStack(causesStackArgs, { workDir: path.dirname(__dirname) + '/src/stacks/causes_stack'});

	await causesStack.setConfig(CAUSES_SERVICE_IMAGE_TAG_INPUT_NAME, { value: imageTag, secret: false });

	await causesStack.workspace.installPlugin("azure-native", "2.3.0");
	await causesStack.workspace.installPlugin("cloudflare", "5.8.0");
	await causesStack.workspace.installPlugin("docker", "4.3.1");
	await causesStack.workspace.installPlugin("github", "5.16.0");

	return causesStack
}

async function createSearchStack(baseStackOutputs: BaseStackReference, imageTag: string) {
	const searchStackArgs: InlineProgramArgs = {
        stackName: "dev",
        projectName: SEARCH_STACK_PROJECT_NAME,
        program: () => searchStackFunction(baseStackOutputs),
	}

	const searchStack = await LocalWorkspace.createOrSelectStack(searchStackArgs, { workDir: path.dirname(__dirname) + '/src/stacks/search_stack'});

	await searchStack.workspace.installPlugin("azure-native", "2.3.0");
	await searchStack.workspace.installPlugin("cloudflare", "5.8.0");
	await searchStack.workspace.installPlugin("docker", "4.3.1");
	// TODO Remove?
	await searchStack.workspace.installPlugin("github", "5.16.0");

	return searchStack
}



type UpArgs = {
	baseOnly: true
} | {
	baseOnly?: false,
	imageTag: string
}

async function up(args: UpArgs) {
	const baseStack = await createBaseStack();
	const baseStackUpResult = await baseStack.up({ onOutput: console.info, color: "always" });

	console.log(`Base stack summary: \n${JSON.stringify(baseStackUpResult.summary.resourceChanges, null, 4)}`);

	if (args.baseOnly) {
		return
	}
	
	const searchStack = await createSearchStack(baseStackUpResult.outputs as BaseStackReference, args.imageTag);
	const searchStackUpResult = await searchStack.up({ onOutput: console.info, color: "always" });
	console.log(`Search stack summary: \n${JSON.stringify(searchStackUpResult.summary.resourceChanges, null, 4)}`);

	const causesStack = await createCausesStack(baseStackUpResult.outputs as BaseStackReference, searchStackUpResult.outputs as SearchStackReference, args.imageTag);
	const causesStackUpResult = await causesStack.up({ onOutput: console.info, color: "always" });
	console.log(`Causes stack summary: \n${JSON.stringify(causesStackUpResult.summary.resourceChanges, null, 4)}`);
}

async function destroy() {
	const baseStack = await createBaseStack();
	const baseStackOriginalOutput = await baseStack.outputs();

	// const causesStack = await createCausesStack(baseStackOriginalOutput as BaseStackReference);
	// const causesStackDestroyResult = await causesStack.destroy({ onOutput: console.info, color: "always" });

	// TODO These cannot be destroyed together, await does not seem to wait!
	// console.log(`Causes stack summary: \n${JSON.stringify(causesStackDestroyResult.summary.resourceChanges, null, 4)}`);

	const baseStackDestroyResult = await baseStack.destroy({ onOutput: console.info, color: "always" });
	console.log(`Base stack summary: \n${JSON.stringify(baseStackDestroyResult.summary.resourceChanges, null, 4)}`);
}

const bootstrapCommand = command({
  name: 'deploy',
  description: 'Deploy base infra required for future deployments',
  version: '0.0.1',
  args: {},
  handler: async (args) => {
	try {
		await up({ baseOnly: true });
		process.exit(0)
	} catch(err) {
		console.error(err)
		process.exit(1)
	}
  },
});

const deployCommand = command({
  name: 'deploy',
  description: 'Deploy all infra',
  version: '0.0.1',
  args: {
	  [CAUSES_SERVICE_IMAGE_TAG_INPUT_NAME]: option({
		type: string,
		long: 'causes-image-tag',
		short: 'c',
		description: 'Tag of the causes service docker image from the registry',
	  }),
  },
  handler: async (args) => {
	try {
		await up({ imageTag: args.causesServiceImageTag });
		process.exit(0)
	} catch(err) {
		console.error(err)
		process.exit(1)
	}
  },
});

const destroyCommand = command({
  name: 'destroy',
  description: 'Destroy all infra',
  version: '0.0.1',
  args: {},
  handler: async (args) => {
	try {
		await destroy()
		process.exit(0)
	} catch(err) {
		console.error(err)
		process.exit(1)
	}
  },
});

const root = subcommands({
	name: 'now-u',
	cmds: {
		bootstrap: bootstrapCommand,
		deploy: deployCommand,
		destroy: destroyCommand,
	}
});

run(root, process.argv.slice(2));
