# Minimal CloudFormation Demo Project for Integrations

## Development

### Setup

This is simple enough to get away with not needing Docker. Just use a virtual
environment and `pip`, with Python ≥3.6.

With builtin `venv` module:

```sh
python -m venv .venv
# Or py -m venv .venv in Windows
.venv/bin/activate
pip install -r requirements.txt
```

Or the excellent `pyenv` tool.

```sh
pyenv virtualenv {version} cirrostratus
pyenv local cirrostratus
pip install -r requirements.txt
```

### Run
The `cirrostratus` package is executable:

```sh
python cirrostratus
```

Which is the same as running `python cirrostratus/__main__.py`.

There's also a `.env` file and `python-dotenv` is installed by the requirements,
so all you have to do is:

```sh
flask run
```

Handy flask commands are also available: `flask routes` and `flask openapi`.

## Layout

The root, where the Flask app is created, is in `cirrostratus/__init__.py`.
OpenAPI 3.0 documentation is in the file `cirrostratus/openapi.yaml`, and
accessible with the conventional command `flask openapi`.


## CloudFormation

There is a script to produce a CloudFormation template in `cirrostratus_cfn`.
`make` is configured to handle the output of this.


### Installation

Couple of extra Python dependencies needed.

```sh
pip install -e .[cfn]
```

### Preview the Template

```sh
flask openapi | python cirrostratus_cfn Cirrostratus --openapi-file -
```

### `make` Operations

If you have `aws` credentials configured, all you need to do is `make deploy`
and you've got a running stack.

+ `make template` produces the template file in `dist/`.
+ `make dist` prepares the Python packages in `dist/`.
+ `make package` runs `aws cloudformation package`, uploads the `dist/` to S3,
  and produces the fully prepared template in `cloudformats/template.yaml`.
+ `make deploy` deploys the packaged template.
