build:
	curl https://links.now-u.com/api/docs/spec.yaml --output links-api-spec.yaml
	openapi-generator-cli generate -i links-api-spec.yaml -g python -c openapi-generator-config.yaml -o generated_client
	cd generated_client && python setup.py install
	
