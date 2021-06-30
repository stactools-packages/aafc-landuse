import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.aafc_landuse import commands
    registry.register_subcommand(commands.create_aafc_landuse_command)


__version__ = "0.2.1a1"
