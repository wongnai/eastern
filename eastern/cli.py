import asyncio
import subprocess
import sys
import time

import click
import click_log
import yaml

from . import formatter, kubectl
from .kubeyml_helper import get_supported_rolling_resources
from .plugin import get_cli_manager, get_plugin_manager


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

    plugin = get_plugin_manager()
    manifest = plugin.chain('deploy_pre_hook', manifest, ctx=ctx)
    out = ctx.obj['kubectl'].apply(data=manifest.encode('utf8'))
    plugin.map_method('deploy_post_hook', manifest, ctx=ctx)

    return out


def wait_for_rolling_deploy(ctx, namespace, manifest, timeout=None):
    wait_resources = get_supported_rolling_resources(manifest)
    for resource in wait_resources:
        ns = resource.namespace or namespace
        name = resource.name
        print_info('Waiting for {} in namespace {} to be completed'.format(
            name, ns))

        ctx.obj['kubectl'].namespace = namespace
        ctx.obj['kubectl'].rollout_wait(name, timeout=timeout)


class Timeout(Exception):
    pass


def wait_for_pod_to_exit(pod_name, kctl, timeout=None):
    time_start = time.time()
    phase = kctl.get_pod_phase(pod_name)

    last_phase = ''

    while phase not in ('', 'Succeeded'):
        if phase != last_phase:
            print_info('Pod {} is in phase {}'.format(pod_name, phase))
            last_phase = phase

        if timeout is not None and time_start + timeout < time.time():
            raise Timeout

        time.sleep(1)
        phase = kctl.get_pod_phase(pod_name)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(prog_name='Project Eastern')
@click.option('--kubectl', default='kubectl', help='Path to kubectl')
@click.option('--context', '-c', help='Kubernetes context to use')
@click.pass_context
@click_log.simple_verbosity_option()
def cli(ctx, context, **kwargs):
    click_log.basic_config()
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
@click.option(
    '--timeout', default=300, help='Wait timeout (default 300s, 0 to disable)')
@click.pass_context
def deploy(ctx, file, namespace, edit, wait, timeout, **kwargs):
    manifest = format_yaml(file, namespace, edit=edit, extra=kwargs['set'])
    result = deploy_from_manifest(ctx, namespace, manifest)

    if not wait or result != 0:
        sys.exit(result)

    if timeout == 0:
        timeout = None

    try:
        wait_for_rolling_deploy(ctx, namespace, manifest, timeout)
    except subprocess.TimeoutExpired:
        print_error('Rollout took too long, exiting...')
        sys.exit(2)


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
@click.option(
    '--timeout', default=300, help='Wait timeout (default 300s, 0 to disable)')
@click.pass_context
def job(ctx, file, namespace, tag, edit, timeout, **kwargs):
    exit_status = 0
    kwargs['set'].append(('IMAGE_TAG', tag))
    manifest = format_yaml(
        file, namespace, edit=edit, extra=kwargs['set'], print=False)

    # Modify the name to contain imageTag
    manifest = list(yaml.load_all(manifest))

    found_job = False
    for item in manifest:
        if item['kind'] != 'Job':
            continue

        found_job = True
        name = '{}-{}'.format(item['metadata']['name'], tag)
        name = name.lower()[:63]
        item['metadata']['name'] = name

    if not found_job:
        print_error('Manifest does not contains any job')
        sys.exit(1)

    manifest = yaml.dump_all(manifest)
    click.echo(manifest)

    # Run the actual deployment
    result = deploy_from_manifest(ctx, namespace, manifest)
    if result != 0:
        sys.exit(result)

    # Wait until job complete
    pod_name = ctx.obj['kubectl'].get_job_pod_name(name)

    if timeout == 0:
        timeout = None

    try:
        wait_for_pod_to_exit(pod_name, ctx.obj['kubectl'], timeout)

        try:
            click.echo(ctx.obj['kubectl'].get_pod_log(pod_name))
        except subprocess.SubprocessError:
            print_error(
                'Cannot read log of pod {}, dumping pod data'.format(pod_name))
            click.echo(yaml.dump(ctx.obj['kubectl'].get_pod(pod_name)))
    except Timeout:
        print_error('Timed out, exiting...')
        exit_status = 2
    except KeyboardInterrupt:
        pass

    print_info('Cleaning up job {}'.format(name))
    result = ctx.obj['kubectl'].delete_job(name)

    if result != 0:
        print_error('Failed to cleanup job "{}"!'.format(name))
        print_info(
            'To cleanup manually, run `{kubectl} delete job {name}`'.format(
                kubectl=' '.join(ctx.obj['kubectl'].get_launch_args()),
                name=name))
        exit_status = 1

    sys.exit(exit_status)


if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

get_cli_manager().map(lambda ext, *args, **kwargs: ext.plugin(cli, ext))
