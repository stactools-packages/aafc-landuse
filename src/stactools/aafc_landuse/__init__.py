import os
import stactools.core

from stactools.aafc_landuse.cog import create_cog
from stactools.aafc_landuse.stac import create_collection, create_item

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data-files"))

__all__ = ["create_collection", "create_item", "create_cog"]

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.aafc_landuse import commands

    registry.register_subcommand(commands.create_aafclanduse_command)


__version__ = "0.2.0"
"""Library version"""
