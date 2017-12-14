import subprocess
import sys
import time

import click
import yaml

from . import formatter, kubectl
from .kubeyml_helper import get_supported_rolling_resources
from .plugin import manager


def print_info(message):
    click.echo(click.style(message, fg='white', bold=True), err=True)


def print_error(message):
    click.echo(click.style(message, fg='red', bold=True), err=True)


def format_yaml(file, namespace, edit=False, print=True, extra=[]):
    env = {
        'NAMESPACE': namespace,
    }
    env.update(**dict(extra))

    manifest = formatter.format(file, env)

    if edit:
        manifest = click.edit(manifest)

        if manifest is None:
            click.echo('File not saved, aborting')
            return
    elif print:
        click.echo(manifest)

    return manifest


def deploy_from_manifest(ctx, namespace, manifest):
    print_info('Deploying to namespace {}...'.format(namespace))

    ctx.obj['kubectl'].namespace = namespace

    manifest = manager.chain('deploy_pre_hook', manifest, ctx=ctx)
    out = ctx.obj['kubectl'].apply(data=manifest.encode('utf8'))
    manager.map_func('deploy_post_hook', manifest, ctx=ctx)

    return out


def wait_for_rolling_deploy(ctx, namespace, manifest):
    wait_resources = get_supported_rolling_resources(manifest)
    for resource in wait_resources:
        ns = resource.namespace or namespace
        name = resource.name
        print_info('Waiting for {} in namespace {} to be completed'.format(
            name, ns))

        ctx.obj['kubectl'].namespace = namespace
        ctx.obj['kubectl'].rollout_wait(name)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(prog_name='Project Eastern')
@click.option('--kubectl', default='kubectl', help='Path to kubectl')
@click.option('--context', '-c', help='Kubernetes context to use')
@click.pass_context
def cli(ctx, context, **kwargs):
    kctl = kubectl.Kubectl(kwargs['kubectl'])
    kctl.context = context
    ctx.obj = {'kubectl': kctl}


def parse_set(ctx, param, value):
    out = []

    for item in value:
        if '=' not in item:
            raise click.BadParameter(
                '{item} must be in format KEY=value'.format(item=item))

        item = item.split('=', maxsplit=1)
        out.append(item)

    return out


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('namespace', default='default')
@click.option(
    '--set',
    '-s',
    callback=parse_set,
    multiple=True,
    help='Additional variables to set')
def generate(file, namespace, **kwargs):
    format_yaml(file, namespace, extra=kwargs['set'])


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('namespace', default='default')
@click.option(
    '--set',
    '-s',
    callback=parse_set,
    multiple=True,
    help='Additional variables to set')
@click.option(
    '--edit',
    '-e',
    is_flag=True,
    help='Edit generated manifest before deploying')
@click.option(
    '--wait/--no-wait', default=True, help='Wait for deployment to finish')
@click.pass_context
def deploy(ctx, file, namespace, edit, wait, **kwargs):
    manifest = format_yaml(file, namespace, edit=edit, extra=kwargs['set'])
    result = deploy_from_manifest(ctx, namespace, manifest)

    if not wait or result != 0:
        sys.exit(result)

    wait_for_rolling_deploy(ctx, namespace, manifest)


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('namespace', default='default')
@click.argument('tag')
@click.option('--set', '-s', callback=parse_set, multiple=True)
@click.option(
    '--edit',
    '-e',
    is_flag=True,
    help='Edit generated manifest before deploying')
@click.pass_context
def job(ctx, file, namespace, tag, edit, **kwargs):
    kwargs['set'].append(('IMAGE_TAG', tag))
    manifest = format_yaml(file, namespace, edit=edit, extra=kwargs['set'])

    # Modify the name to contain imageTag
    manifest = list(yaml.load_all(manifest))
    if len(manifest) > 1:
        raise click.BadParameter('Manifest must have exactly one document')

    manifest = manifest[0]
    if manifest['kind'] != 'Job':
        raise click.BadParameter('Manifest file is not a job')

    name = '{}-{}'.format(manifest['metadata']['name'], tag)
    name = name[:63]
    manifest['metadata']['name'] = name
    manifest = yaml.dump(manifest)

    # Run the actual deployment
    result = deploy_from_manifest(ctx, namespace, manifest)
    if result != 0:
        sys.exit(result)

    # Wait until job complete
    pod_name = ctx.obj['kubectl'].get_job_pod_name(name)

    phase = ctx.obj['kubectl'].get_pod_phase(pod_name)

    last_phase = ''
    while phase not in ('', 'Succeeded'):
        if phase != last_phase:
            print_info('Pod {} is in phase {}'.format(pod_name, phase))
            last_phase = phase

        time.sleep(1)
        phase = ctx.obj['kubectl'].get_pod_phase(pod_name)

    try:
        click.echo(ctx.obj['kubectl'].get_pod_log(pod_name))
    except subprocess.SubprocessError:
        print_error(
            'Cannot read log of pod {}, dumping pod data'.format(pod_name))
        click.echo(yaml.dump(ctx.obj['kubectl'].get_pod(pod_name)))

    print_info('Cleaning up job {}'.format(name))
    result = ctx.obj['kubectl'].delete_job(name)

    if result != 0:
        print_error('Failed to cleanup job "{}"!'.format(name))
        print_info(
            'To cleanup manually, run `{kubectl} delete job {name}`'.format(
                kubectl=' '.join(ctx.obj['kubectl'].get_launch_args()),
                name=name))


manager.map_method('cli_hook', cli)
