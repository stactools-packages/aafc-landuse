import os
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.aafc_landuse.commands import create_aafclanduse_command
from stactools.aafc_landuse.constants import JSONLD_HREF
from stactools.aafc_landuse.utils import AssetManager

TEST_ITEM = "https://www.agr.gc.ca/atlas/data_donnees/lcv/aafcLand_Use/tif/2010/IMG_AAFC_LANDUSE_Z07_2010.zip"  # noqa


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_aafclanduse_command]

    def test_create_collection(self):
        with TemporaryDirectory() as tmp_dir:
            result = self.run_command(
                ["aafclanduse", "create-collection", "-d", tmp_dir]
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(os.path.join(tmp_dir, jsons[0]))

            collection.validate()

    def test_create_cog_and_item(self):
        with TemporaryDirectory() as tmp_dir:
            # Create a COG and item
            with AssetManager(TEST_ITEM) as src:

                result = self.run_command(
                    ["aafclanduse", "create-cog", src.path, tmp_dir]
                )
                self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

                cog_path = os.path.join(
                    tmp_dir, os.path.basename(src.path)[:-4] + "_cog.tif"
                )

                self.assertTrue(os.path.isfile(cog_path))

                cmd = [
                    "aafclanduse",
                    "create-item",
                    "-d",
                    tmp_dir,
                    "-c",
                    cog_path,
                    "-m",
                    JSONLD_HREF,
                ]
                result = self.run_command(cmd)
                self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            # Validate item
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

            asset = item.assets["landuse"]

            self.assertIn("data", asset.roles)

            # Projection Extension
            self.assertIn("proj:epsg", asset.extra_fields)
            self.assertIn("proj:bbox", asset.extra_fields)
            self.assertIn("proj:transform", asset.extra_fields)
            self.assertIn("proj:shape", asset.extra_fields)
            self.assertIn("proj:bbox", item.properties)
            self.assertIn("proj:transform", item.properties)
            self.assertIn("proj:shape", item.properties)

            # File Extension
            self.assertIn("file:size", asset.extra_fields)
            self.assertIn("file:values", asset.extra_fields)
            self.assertGreater(len(asset.extra_fields["file:values"]), 0)

            # Raster Extension
            self.assertIn("raster:bands", asset.extra_fields)
            self.assertEqual(len(asset.extra_fields["raster:bands"]), 1)
            self.assertIn("nodata", asset.extra_fields["raster:bands"][0])
            self.assertIn("sampling", asset.extra_fields["raster:bands"][0])
            self.assertIn("data_type", asset.extra_fields["raster:bands"][0])
            self.assertIn("spatial_resolution", asset.extra_fields["raster:bands"][0])

            # Label Extension
            self.assertIn("labels", asset.roles)
            self.assertIn("labels-raster", asset.roles)

            item.validate()
