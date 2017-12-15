# Project Eastern

[![Travis](https://api.travis-ci.org/wongnai/eastern.svg?branch=master)](https://travis-ci.org/wongnai/eastern)
[![GitHub license](https://img.shields.io/github/license/wongnai/eastern.svg)](https://github.com/wongnai/eastern/blob/master/LICENSE)

A Kubernetes templating and deployment tool.

## Table of Contents

* [Features](#features)
* [Installation](#installation)
  * [Installing from Git](#installing-from-git)
* [Usage](#usage)
  * [Template language](#template-language)
  * [Deploy](#deploy)
  * [Deploy jobs](#deploy-jobs)
* [Roadmap](#roadmap)
* [License](#license)

## Features

* Simple, logicless template engine designed for YAML
* Work with multiple environments
* In use in production at [Wongnai](https://www.wongnai.com)

## Installation

Note that Eastern requires `kubectl`.

### Running from Docker Image

Eastern is available on [Docker Hub](https://hub.docker.com/r/wongnai/eastern/) for continuous delivery users.

```sh
docker run -v `pwd`:/projects/ --rm wongnai/eastern eastern generate /projects/kubernetes.yaml
```

### Installing from Git

1. Clone this repository
2. Run `python3 setup.py install`. You might to run this as root.
3. Run `eastern` to verify that it is installed.

## Usage
### Template language 
At its core, Eastern is a YAML templating tool. Eastern provides the following commands as YAML comment.

- `load? file_1.yaml, file_2.yaml ...`: Load the first file available
- `load! file_1.yaml, file_2.yaml ...`: Same as `load?` but throw when no file is loaded.

The file name and contents may contains variable interpolation. Available variable is

- `${NAMESPACE}`: Name of namespace

Additional variables can be passed by `-s var=value`.

For example:

```yaml
image: wongnai/eastern:${IMAGE_TAG}
env:
  # load! env-${NAMESPACE}.yaml, env.yaml
```

See full deployment example in the [example](example/) folder.

Once you have written a template, test it with `eastern generate path/to/file.yaml namespace -s IMAGE_TAG=2.0`.

### Deploy

To deploy, run `eastern deploy path/to/file.yaml namespace`.

Available options:

- `--set var=value` (`-s`): Set additional template variables
- `--edit` (`-e`): Edit resulting YAML before deploying
- `--no-wait`: Exit after running `kubectl` without waiting for rolling deploy

### Deploy jobs
Eastern comes with [Job](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/) deployment tool.

To start a job, run `eastern job path/to/file.yaml namespace image_tag`. The file must have the job as its only document. Eastern will add `image_tag` as job suffix, deploy, wait until job's completion and remove the job.

Supplied `image_tag` is available in the template as `${IMAGE_TAG}`.

## Roadmap

While Eastern has been used in production at Wongnai for months, this open source release still need some works to be done before we could say that it is "1.0".

- [X] Setup Docker Hub build
- [X] Rewrite tests
- [X] Setup Travis
- [X] Plugin support
- [ ] Migrate internal deployments to open source edition (we may have breaking changes before this point)
- [ ] Release on PyPI

## License
(C) 2017 Wongnai Media Co, Ltd.

Eastern is licensed under [MIT License](LICENSE)
