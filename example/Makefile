all:

dist: project_name/** setup.py
	pip install -t dist .[prod]

dist/openapi.yaml: project_name/openapi.yaml
	mkdir -p dist
	cp project_name/openapi.yaml > dist/openapi.yaml

dist/template.yaml: dist/openapi.yaml project_name/cfn.py
	mkdir -p dist
	i9n-cfn-gen ProjectName \
		--openapi dist/openapi.yaml \
		--secret BACKEND_UID "Backend User Identifier" "" \
    --plugin project_name.cfn:items \
		> dist/template.yaml

.ONESHELL:
cloudformation/template.yaml: dist dist/template.yaml
	cd dist
	aws cloudformation package \
		--template template.yaml \
		--s3-bucket ${S3_BUCKET} \
		--s3-prefix ProjectName \
		--output-template ../cloudformation/template.yaml

template: dist/template.yaml

package: cloudformation/template.yaml

clean:
	rm -rf dist/ cloudformation/template.yaml
