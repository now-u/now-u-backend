import * as pulumi from "@pulumi/pulumi";

export function getCurrentStack() {
	return new pulumi.StackReference(
		`${pulumi.getOrganization()}/${pulumi.getProject()}/${pulumi.getStack()}`
	)
}
