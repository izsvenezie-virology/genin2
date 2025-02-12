import click, genin2.genin2_core
from click import File
from genin2.genin2_core import __version__, __author__, __contact__, run


@click.command('genin2')
@click.help_option('-h', '--help')
@click.version_option(__version__, '-v', '--version', message=f'%(prog)s, version %(version)s, by {__author__} ({__contact__})')
@click.argument('input-file', type=File('r'))
@click.argument('output-file', type=File('w'))
def start_cli(input_file: File, output_file: File):
    run(input_file, output_file)
