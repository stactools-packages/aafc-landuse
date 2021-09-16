import stactools.core

from stactools.aafc_landuse.stac import create_collection, create_item
from stactools.aafc_landuse.cog import create_cog

__all__ = ["create_collection", "create_item", "create_cog"]

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.aafc_landuse import commands

    registry.register_subcommand(commands.create_aafclanduse_command)


__version__ = "0.2.0"
"""Library version"""
