
import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.aafc_landuse import commands
    registry.register_subcommand(commands.create_aafclanduse_command)


__version__ = '0.2.0'
"""Library version"""
