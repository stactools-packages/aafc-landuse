import os
from tempfile import TemporaryDirectory

import pystac

from stactools.aafc_landuse.commands import create_aafclanduse_command
from stactools.testing import CliTestCase

TEST_ITEM = "https://www.agr.gc.ca/atlas/data_donnees/lcv/aafcLand_Use/tif/2010/IMG_AAFC_LANDUSE_Z07_2010.zip"  # noqa


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_aafclanduse_command]

    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:
            cmd = ['aafclanduse', 'create-item', TEST_ITEM, tmp_dir]
            self.run_command(cmd)

            cogs = [p for p in os.listdir(tmp_dir) if p.endswith('_cog.tif')]
            self.assertEqual(len(cogs), 1)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
