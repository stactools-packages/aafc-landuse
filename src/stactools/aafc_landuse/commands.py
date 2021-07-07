import click
import logging
import os

from stactools.aafc_landuse import stac
from stactools.aafc_landuse import cog
from stactools.aafc_landuse import utils
from stactools.aafc_landuse.constants import JSONLD_HREF

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
        "-m",
        "--metadata",
        help="The url to the metadata jsonld",
        default=JSONLD_HREF,
    )
    def create_collection_command(dst: str, metadata: str):
        """Creates a STAC Collection from AAFC Land Use metadata

        Args:
            dst (str): Directory to create the collection json
            metadata (str): Path to a jsonld metadata file - provided by AAFC
        Returns:
            Callable
        """
        metadata = utils.get_metadata(metadata)

        collection = stac.create_collection(metadata)

    @aafclanduse.command(
        "create-item",
        short_help="Create a STAC item from an AAFC Land Use tif",
    )
    @click.argument("src")
    @click.argument("dst")
    @click.option(
        "-m",
        "--metadata",
        help="The url to the metadata jsonld",
        default=JSONLD_HREF,
    )
    def create_item_command(src: str, dst: str, metadata: str):
        """Creates a STAC Item from an AAFC Land Use raster and
        accompanying metadata file.

        Args:
            src (str): Path to an AAFC Land Use tif
            dst (str): Directory where a COG and STAC item json will be created
            metadata (str): Path to a jsonld metadata file - provided by AAFC
        Returns:
            Callable
        """
        metadata = utils.get_metadata(metadata)

        # Access/download src tif and create a COG
        with utils.AssetManager(src) as asset:
            asset_tif = asset.path
            cog_path = os.path.join(
                dst,
                os.path.splitext(os.path.basename(asset_tif))[0] + "_cog.tif")
            cog.create_cog(asset_tif, cog_path, dry_run=False)

        # Create stac item
        json_path = cog_path[:-8] + '.json'
        stac.create_item(metadata, json_path, cog_path)

    return aafclanduse
