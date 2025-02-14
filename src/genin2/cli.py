import click
from genin2.genin2_core import __version__, __author__, __contact__, run


@click.command(epilog='')
@click.help_option('-h', '--help')
@click.version_option(__version__, '-v', '--version', message=f'%(prog)s, version %(version)s, by {__author__} ({__contact__})')
@click.option('-i', '--input-file', type=click.File('r'), help='Input FASTA', required=True)
@click.option('-o', '--output-file', type=click.File('w'), help='Output TSV', required=True)
@click.option('--loglevel', type=click.Choice(['dbg', 'inf', 'wrn', 'err'], case_sensitive=False), default='inf', help='Verbosity of the logging messages')
@click.option('--min-seq-cov', type=click.FloatRange(0, 1), help='The minimum fraction of a sequence that needs to be valid (no Ns) to be accepted for prediction', default=0.9, show_default=True)
def start_cli(input_file: click.File, output_file: click.File, **kwargs):
    run(input_file, output_file, **kwargs)
