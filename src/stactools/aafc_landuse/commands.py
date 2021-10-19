import logging
import os

import click

from stactools.aafc_landuse import cog, stac
from stactools.aafc_landuse.constants import METADATA_URL, THUMBNAIL_URL

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
        """Create a COG from an AAFC Land Use source .tif

        Args:
            source (str): Source .tif
            destination (str): Output directory for COG
        """
        cog.create_cog(source, destination)

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
        help="URL to the AAFC metadata json",
        default=METADATA_URL,
    )
    @click.option(
        "-t",
        "--thumbnail",
        help="URL to a collection thumbnail",
        default=THUMBNAIL_URL,
    )
    def create_collection_command(destination: str, metadata: str,
                                  thumbnail: str):
        """Creates a STAC Collection from AAFC Land Use metadata

        Args:
            destination (str): Directory to create the collection json
            metadata (str, optional): Path to json metadata file - provided by AAFC
            thumbnail (str, optional): Path to a thumbnail

        Returns:
            Callable
        """
        # Collect the metadata as a dict and create the collection
        collection = stac.create_collection(metadata, thumbnail)

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
    @click.option("-c", "--cog", required=True, help="COG href")
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json",
    )
    @click.option(
        "-m",
        "--metadata",
        required=True,
        help="The url to the metadata description.",
        default=METADATA_URL,
    )
    def create_item_command(cog: str, destination: str, metadata: str):
        """Creates a STAC Item from a cogified AAFC Land Use raster and
        accompanying metadata file.

        :Note: The item title is parsed from the cog file name, which should be
        created using the `create-cog` command prior to creating an item

        Args:
            cog (str): Path to an AAFC Land Use tif
            destination (str): Directory where a COG and STAC item json will be created
            metadata (str): Path to a jsonld metadata file - provided by AAFC
        Returns:
            Callable
        """
        item = stac.create_item(cog, metadata)

        # Set the href, save, and validate
        output_path = os.path.join(destination,
                                   os.path.basename(cog)[:-4] + ".json")
        item.set_self_href(output_path)
        item.make_asset_hrefs_relative()
        item.save_object()
        item.validate()

    return aafclanduse
