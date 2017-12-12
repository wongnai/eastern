# Example Sentry installation

**Note that this is NOT written for production use**. It may not even run!

In this example, we will deploy [Sentry](https://docs.sentry.io/server/installation/docker/), an exception catcher to our cluster.

## Goal of this example

We will install 2 instances of Sentry on namespace `default` and `prod`. It is assumed that there is a compatible PostgreSQL server running in the namespace already.

## Project layout

Eastern doesn't have any enforced project layout; all files can be placed in this folder. In our case we use a monorepo that store all projects' configuration, each similar to this folder.

The overall layout is

```
projects
|- sentry
|  |- overrides
|  |  \- env.yaml
|  \ kubernetes.yaml
\- frontend
   |- overrides
   |  \- env.yaml
   \ kubernetes.yaml
```

## Understanding the files

First we write the main deployment file, [sentry.yaml](sentry.yaml). Notice that the image tag is a placeholder `${IMAGE_TAG}` and the environment is loaded from `overrides/env-${NAMESPACE}.yaml` or `overrides/env.yaml`.

In [overrides/env-prod.yaml](overrides/env-prod.yaml) and [overrides/env.yaml](overrides/env.yaml) we write the environment variables for production and development environment respectively. We could also name the development environment file `overrides/env-default.yaml`, but having a default values would be easier to use.

On the topmost section of the main deployment file we use YAML documents to load [overrides/ingress.yaml](overrides/ingress.yaml) (with production override) and [overrides/service.yaml](overrides/service.yaml).

## Deploying

To preview, run `eastern generate sentry.yaml -s IMAGE_TAG=8.22`. After checking that this is what you expect, run

- `eastern deploy sentry.yaml -s IMAGE_TAG=8.22` to deploy to default namespace
- `eastern deploy sentry.yaml prod -s IMAGE_TAG=8.22` to deploy to prod namespace
