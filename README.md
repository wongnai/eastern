# Project Eastern V2

[![Travis](https://api.travis-ci.com/seehait/eastern.svg?branch=master)](https://travis-ci.com/seehait/eastern)
[![GitHub license](https://img.shields.io/github/license/seehait/eastern.svg)](https://github.com/seehait/eastern/blob/master/LICENSE)
[![Read the Docs](https://readthedocs.org/projects/eastern-v2/badge/?version=latest)](https://eastern-v2.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/eastern-v2.svg)](https://pypi.python.org/pypi/eastern-v2)
[![Docker Hub](https://img.shields.io/docker/build/seehait/eastern.svg)](https://hub.docker.com/r/seehait/eastern/)

A Kubernetes templating and deployment tool.

## Table of Contents

- [Project Eastern V2](#project-eastern-v2)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Installing from PyPI](#installing-from-pypi)
    - [Running from Docker Image](#running-from-docker-image)
    - [Installing from Git](#installing-from-git)
  - [Usage](#usage)
    - [Template language](#template-language)
    - [Deploy](#deploy)
    - [Deploy jobs](#deploy-jobs)
  - [Plugin](#plugin)
  - [License](#license)

## Features

* Simple, logicless template engine designed for YAML
* Work with multiple environments
* Extensible plugin architecture

## Installation

Note that Eastern requires `kubectl`.

### Installing from PyPI

Run `pip install eastern` to install.

### Running from Docker Image

Eastern V2 is available on [Docker Hub](https://hub.docker.com/r/seehait/eastern/) for continuous delivery users.

```sh
docker run -v `pwd`:/projects/ --rm seehait/eastern eastern generate /projects/kubernetes.yaml
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
image: seehait/eastern:${IMAGE_TAG}
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

## Plugin
Eastern is extensible. We use Eastern plugins ourselves. The API docs is available on [Read the Docs](https://eastern-v2.readthedocs.io/en/latest/).

## License
(C) 2019 Seehait Chockthanyawat
Originally by 2017 Wongnai Media Co, Ltd.

Eastern is licensed under [MIT License](LICENSE)
