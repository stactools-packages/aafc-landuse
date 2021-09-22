import logging
import os

import click

from stactools.aafc_landuse import cog, stac, utils

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
    @click.argument("destination")
    def create_collection_command(destination: str):
        """Creates a STAC Collection from AAFC Land Use metadata

        Args:
            destination (str): Directory to store output collection json
        Returns:
            Callable
        """
        # Collect the metadata as a dict and create the collection
        metadata_dict = utils.get_metadata()
        output_path = os.path.join(destination, "aafc_landuse_collection.json")
        collection = stac.create_collection(metadata_dict, output_path)

        # Set the destination
        collection.set_self_href(output_path)
        collection.normalize_hrefs(destination)

        # Save and validate
        collection.save()
        collection.validate()

    @aafclanduse.command(
        "create-item",
        short_help="Create a STAC item from an AAFC Land Use tif",
    )
    @click.argument("destination")
    @click.argument("cog")
    def create_item_command(destination: str, cog: str):
        """Creates a STAC Item from a cogified AAFC Land Use raster and
        accompanying metadata file.

        :Note: The item title is parsed from the cog file name, which should be
        created using the `create-cog` command prior to creating an item

        Args:
            destination (str): Directory to store the item json
            cog (str): Path to an AAFC Land Use tif
        Returns:
            Callable
        """
        # Collect metadata and create item
        jsonld_metadata = utils.get_metadata()
        jsonld_metadata["title"] = os.path.basename(cog)[:-4]

        output_path = os.path.join(destination,
                                   f"{os.path.basename(cog)[:-4]}.json")

        item = stac.create_item(jsonld_metadata, output_path, cog)

        # Set the href, save, and validate
        item.set_self_href(output_path)
        item.make_asset_hrefs_relative()
        item.save_object()
        item.validate()

    return aafclanduse
