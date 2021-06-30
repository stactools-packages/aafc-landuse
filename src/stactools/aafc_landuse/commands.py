import click
import logging

logger = logging.getLogger(__name__)


def create_aafc_landuse_command(cli):
    """Creates the aafclanduse command line utility."""
    @cli.group(
        "aafclanduse",
        short_help=(
            "Commands for working with 1990, 2000 and 2010 Canada Land Use data"
        ),
    )
    def aafc_landuse():
        pass

    @aafc_landuse.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option("--output",
                  required=True,
                  help="The output directory to write the COGs to.")
    def create_cogs(path_to_cogs: str):
        # Fill this in
        return False

    return aafc_landuse
