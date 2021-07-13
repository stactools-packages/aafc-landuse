import click
import logging
import os

from stactools.aafc_landuse.constants import LANDUSE_ID, JSONLD_HREF
from stactools.aafc_landuse import stac, cog, utils

logger = logging.getLogger(__name__)


def create_aafclanduse_command(cli):
    """Creates a command line utility for working with
    AAFC Land Use categorical rasters
    """
    @cli.group(
        "aafclanduse",
        short_help=("Commands for working with AAFC Land Use data"),
    )
    def aafclanduse():
        pass

    @aafclanduse.command(
        "create-collection",
        short_help="Creates a STAC collection from AAFC Land Use metadata",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json",
    )
    @click.option(
        "-m",
        "--metadata",
        help="The url to the metadata jsonld",
        default=JSONLD_HREF,
    )
    def create_collection_command(destination: str, metadata: str):
        """Creates a STAC Collection from AAFC Land Use metadata

        Args:
            destination (str): Directory to create the collection json
            metadata (str): Path to a jsonld metadata file - provided by AAFC
        Returns:
            Callable
        """
        metadata = utils.get_metadata(metadata)

        output_path = os.path.join(destination, f"{LANDUSE_ID}.json")

        stac.create_collection(metadata, output_path)

    @aafclanduse.command(
        "create-item",
        short_help="Create a STAC item from an AAFC Land Use tif",
    )
    @click.option(
        "-s",
        "--source",
        required=True,
        help="Path to an AAFC Land Use tif",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json and COG",
    )
    @click.option(
        "-m",
        "--metadata",
        help="The url to the metadata description.",
        default=JSONLD_HREF,
    )
    def create_item_command(source: str, destination: str, metadata: str):
        """Creates a STAC Item from an AAFC Land Use raster and
        accompanying metadata file.

        Args:
            source (str): Path to an AAFC Land Use tif
            destination (str): Directory where a COG and STAC item json will be created
            metadata (str): Path to a jsonld metadata file - provided by AAFC
        Returns:
            Callable
        """
        metadata = utils.get_metadata(metadata)

        # Access/download src tif and create a COG
        with utils.AssetManager(source) as asset:
            asset_tif = asset.path
            cog_path = os.path.join(
                destination,
                os.path.splitext(os.path.basename(asset_tif))[0] + "_cog.tif",
            )
            cog.create_cog(asset_tif, cog_path, dry_run=False)

        # Create stac item
        json_path = cog_path[:-8] + ".json"
        stac.create_item(metadata, json_path, cog_path)

    return aafclanduse
