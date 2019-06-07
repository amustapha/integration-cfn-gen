all:

dist: cirrostratus setup.py
	pip install -t dist .[prod]

dist/openapi.yaml: cirrostratus/openapi.yaml
	mkdir -p dist
	python -m flask openapi > dist/openapi.yaml

dist/template.yaml: dist/openapi.yaml cirrostratus_cfn
	mkdir -p dist
	python -m cirrostratus_cfn Cirrostratus --openapi dist/openapi.yaml > dist/template.yaml

.ONESHELL:
cloudformation/template.yaml: dist dist/template.yaml
	cd dist
	aws cloudformation package \
		--template template.yaml \
		--s3-bucket bc-wcf-dev-lambda-bin \
		--s3-prefix Cirrostratus \
		--output-template ../cloudformation/template.yaml

template: dist/template.yaml

package: cloudformation/template.yaml

deploy: cloudformation/template.yaml
	aws cloudformation deploy \
		--stack-name cirrostratus \
		--template cloudformation/template.yaml \
		--capabilities CAPABILITY_IAM

clean:
	rm -rf dist
	rm cloudformation/template.yaml
