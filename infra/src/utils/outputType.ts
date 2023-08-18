export type StackCreationOutput<T> = {
	[K in keyof T]: {
		value: T[K];
		secret: boolean;
	}
}
