import os
from tempfile import TemporaryDirectory
import unittest

import pystac

from stactools.aafc_landuse.constants import JSONLD_HREF
from stactools.aafc_landuse import utils
from stactools.aafc_landuse import cog
from stactools.aafc_landuse import stac


TEST_ITEM = "https://www.agr.gc.ca/atlas/data_donnees/lcv/aafcLand_Use/tif/2010/IMG_AAFC_LANDUSE_Z07_2010.zip"  # noqa


class StacTest(unittest.TestCase):
    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:
            metadata = utils.get_metadata(JSONLD_HREF)

            with utils.AssetManager(TEST_ITEM) as asset:
                asset_tif = asset.path
                cog_path = os.path.join(
                    tmp_dir, os.path.splitext(os.path.basename(asset_tif))[0] + "_cog.tif"
                )
                cog.create_cog(asset_tif, cog_path, dry_run=False)

            # Create stac item
            json_path = cog_path[:-8] + '.json'
            stac.create_item(metadata, json_path, cog_path)

            cogs = [p for p in os.listdir(tmp_dir) if p.endswith('_cog.tif')]
            self.assertEqual(len(cogs), 1)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
