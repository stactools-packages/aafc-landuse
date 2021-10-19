import os
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.aafc_landuse.commands import create_aafclanduse_command
from tests import test_data


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_aafclanduse_command]

    def test_create_collection(self):
        with TemporaryDirectory() as tmp_dir:
            result = self.run_command(
                ["aafclanduse", "create-collection", tmp_dir])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p == "collection.json"]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(os.path.join(tmp_dir, jsons[0]))

            collection.validate()

    def test_create_cog_and_item(self):
        test_path = test_data.get_path("data-files")
        test_tif = next((os.path.join(test_path, d)
                         for d in os.listdir(test_path)
                         if d.lower().endswith(".tif")))

        with TemporaryDirectory() as tmp_dir:
            test_path = test_data.get_path("data-files")
            test_path = next((os.path.join(test_path, f)
                              for f in os.listdir(test_path)
                              if f.lower().endswith(".tif")))

            # Create a COG and item
            result = self.run_command(
                ["aafclanduse", "create-cog", test_path, tmp_dir])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            cog_path = os.path.join(
                tmp_dir,
                os.path.basename(test_path)[:-4] + "_cog.tif")
            self.assertTrue(os.path.isfile(cog_path))

            cmd = ["aafclanduse", "create-item", "-c", cog_path, "-d", tmp_dir]
            result = self.run_command(cmd)
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

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
            self.assertIn("spatial_resolution",
                          asset.extra_fields["raster:bands"][0])

            # Label Extension
            self.assertIn("labels", asset.roles)
            self.assertIn("labels-raster", asset.roles)

            item.validate()
