import sys

import click

from . import deploy, fileformatter, kubectl

def print_info(message):
    click.echo(click.style(message, fg='white', bold=True), err=True)

@click.group(context_settings={
    'help_option_names': ['-h', '--help']
})
@click.version_option(prog_name='Project Eastern')
@click.option('--kubectl', default='kubectl', help='Path to kubectl')
@click.option('--context', '-c', help='Kubernetes context to use')
@click.pass_context
def cli(ctx, context, **kwargs):
    kctl = kubectl.Kubectl(kwargs['kubectl'])
    kctl.context = context
    ctx.obj = {
        'kubectl': kctl
    }

def parse_set(ctx, param, value):
    out = []

    for item in value:
        if '=' not in item:
            raise click.BadParameter('{item} must be in format KEY=value'.format(item=item))

        item = item.split('=', maxsplit=1)
        out.append(item)

    return out

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('namespace')
@click.argument('tag')
@click.option('--set', '-s', callback=parse_set, multiple=True)
def generate(file, namespace, tag, **kwargs):
    env = {
        'NAMESPACE': namespace,
        'IMAGE_TAG': tag,
    }
    env.update(kwargs['set'])

    manifest = fileformatter.format(file, env)
    click.echo(manifest)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('namespace')
@click.argument('tag')
@click.option('--set', '-s', callback=parse_set, multiple=True)
@click.option('--edit', '-e', is_flag=True)
@click.pass_context
def deploy(ctx, file, namespace, tag, edit, wait, **kwargs):
    env = {
        'NAMESPACE': namespace,
        'IMAGE_TAG': tag,
    }
    env.update(kwargs['set'])

    manifest = fileformatter.format(file, env)

    if edit:
        manifest = click.edit(manifest)

        if manifest is None:
            click.echo('File not saved, aborting')
            return
    else:
        click.echo(manifest)

    print_info('Deploying to namespace {}...'.format(namespace))

    ctx.obj['kubectl'].namespace = namespace
    result = ctx.obj['kubectl'].apply(data=manifest.encode('utf8'))

    if not wait or result.returncode != 0:
        sys.exit(result.returncode)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('namespace')
@click.argument('tag')
@click.option('--set', '-s', callback=parse_set, multiple=True)
def job(file, namespace, tag, **kwargs):
    print('Job')

