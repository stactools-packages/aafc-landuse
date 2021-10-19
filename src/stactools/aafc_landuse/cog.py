import os
import re

from stactools.core.utils.convert import cogify


def create_cog(source: str, destination: str):
    """Create a COG from an AAFC Land Use source .tif

    Args:
        source (str): Path to source .tif
        destination (str): Destination directory to save the resulting COG
    """
    cog_name = os.path.basename(source)[:-4] + "_cog.tif"
    cog_destination = os.path.join(destination, cog_name)

    # Ensure a year can be extracted from the path
    match = re.search(r"LU\d{4}", cog_name)
    if not match:
        raise ValueError(
            "The source .tif should originate from the source AAFC " +
            "data so a year may be extracted from the name")

    cogify(source, cog_destination, ["-co", "compress=LZW"])
