import click
from genin2.genin2_core import __version__, __author__, __contact__, run, print_model_info


@click.command(epilog='')
@click.help_option('-h', '--help')
@click.version_option(__version__, '-v', '--version', message=f'%(prog)s, version %(version)s, by {__author__} ({__contact__})')
@click.argument('input_file', type=click.File('r'), default='-')
@click.option('--model-info', is_flag=True, help='Show information about models and exit')
@click.option('-o', '--output-file', type=click.File('w'), help='Output TSV', default='-')
@click.option('--loglevel', type=click.Choice(['dbg', 'inf', 'wrn', 'err'], case_sensitive=False), default='wrn', help='Verbosity of the logging messages', show_default=True)
@click.option('--min-seq-cov', type=click.FloatRange(0, 1), help='The minimum accepted sequence coverage for each gene segment', default=0.7, show_default=True)
def start_cli(input_file: click.File, output_file: click.File, **kwargs):
    if kwargs['model_info']:
        print_model_info()
    else:
        run(input_file, output_file, **kwargs)
