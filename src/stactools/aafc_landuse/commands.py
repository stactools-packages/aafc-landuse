import click
import logging
import os

from stactools.aafc_landuse.constants import JSONLD_HREF
from stactools.core.utils.convert import cogify
from stactools.aafc_landuse import stac, utils

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
        "create-cog",
        short_help="Creates a COG from an AAFC Land Use .tif",
    )
    @click.argument("source")
    @click.argument("destination")
    def create_cog_command(source: str, destination: str):
        """Create a COG from an AAFC Land Use .tif

        Args:
            source (str): Source .tif
            destination (str): Output destination for COG
        """
        cogify(source, destination, ["-co", "compress=LZW"])

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
        # Collect the metadata as a dict and create the collection
        metadata_dict = utils.get_metadata(metadata)
        collection = stac.create_collection(metadata_dict, metadata)

        # Set the destination
        output_path = os.path.join(destination, "collection.json")
        collection.set_self_href(output_path)
        collection.normalize_hrefs(destination)

        # Save and validate
        collection.save()
        collection.validate()

    @aafclanduse.command(
        "create-item",
        short_help="Create a STAC item from an AAFC Land Use tif",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json",
    )
    @click.option("-c", "--cog", required=True, help="COG href")
    @click.option(
        "-m",
        "--metadata",
        required=True,
        help="The url to the metadata description.",
        default=JSONLD_HREF,
    )
    def create_item_command(destination: str, cog: str, metadata: str):
        """Creates a STAC Item from an AAFC Land Use raster and
        accompanying metadata file.

        Args:
            destination (str): Directory where a COG and STAC item json will be created
            cog (str): Path to an AAFC Land Use tif
            metadata (str): Path to a jsonld metadata file - provided by AAFC
        Returns:
            Callable
        """
        # Collect metadata and create item
        jsonld_metadata = utils.get_metadata(metadata)
        item = stac.create_item(jsonld_metadata, metadata, cog)

        # Set the href, save, and validate
        output_path = os.path.join(destination,
                                   os.path.basename(cog)[:-4] + ".json")
        item.set_self_href(output_path)
        item.make_asset_hrefs_relative()
        item.save_object()
        item.validate()

    return aafclanduse
