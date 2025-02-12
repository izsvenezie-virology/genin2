import click, genin2, sys
from click import File
from genin2 import __version__, __author__, __contact__


@click.command()
@click.help_option('-h', '--help')
@click.version_option(__version__, '-v', '--version', message=f'%(prog)s, version %(version)s, by {__author__} ({__contact__})')
@click.argument('input-file', type=File('r'))
@click.argument('output-file', type=File('w'))
def start_cli(input_file: File, output_file: File):
    genin2.run(input_file, output_file)