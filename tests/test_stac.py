import unittest
import os
from tempfile import TemporaryDirectory
import re

from pystac.utils import datetime_to_str

from stactools.aafc_landuse import cog, stac
from tests import test_data


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        # Create stac collection
        collection = stac.create_collection()
        collection.set_self_href("mock-path")

        item_asset = collection.extra_fields["item_assets"]["landuse"]
        summaries = collection.summaries.to_dict()

        self.assertIn("metadata", collection.assets)
        self.assertIn("data", item_asset["roles"])

        # Projection Extension
        self.assertIn("proj:epsg", item_asset)
        self.assertIn("proj:epsg", summaries)

        # File Extension
        self.assertIn("file:values", item_asset)
        self.assertGreater(len(item_asset["file:values"]), 0)

        # Raster Extension
        self.assertIn("raster:bands", item_asset)
        self.assertIn("nodata", item_asset["raster:bands"][0])
        self.assertIn("sampling", item_asset["raster:bands"][0])
        self.assertIn("data_type", item_asset["raster:bands"][0])
        self.assertIn("spatial_resolution", item_asset["raster:bands"][0])

        # Label Extension
        self.assertIn("labels", item_asset["roles"])
        self.assertIn("labels-raster", item_asset["roles"])

        self.assertIn("label:type", summaries)
        self.assertIn("label:tasks", summaries)
        self.assertIn("label:classes", summaries)

        self.assertIn("label:type", item_asset)
        self.assertIn("label:tasks", item_asset)
        self.assertIn("label:properties", item_asset)
        self.assertIn("label:classes", item_asset)

        collection.validate()

    def test_create_cog_and_item(self):
        with TemporaryDirectory() as tmp_dir:
            test_path = test_data.get_path("data-files")
            paths = [
                os.path.join(test_path, d)
                for d in os.listdir(test_path)
                if d.lower().endswith(".tif")
            ]

            for path in paths:
                cog.create_cog(path, tmp_dir)

                cog_name = os.path.basename(path)[:-4] + "_cog.tif"

                cog_path = next(
                    (
                        os.path.join(tmp_dir, f)
                        for f in os.listdir(tmp_dir)
                        if f == cog_name
                    ),
                    None,
                )
                self.assertIsNotNone(cog_path)

                item = stac.create_item(cog_path)

                item.set_self_href("mock-path")

                cog_id = os.path.basename(cog_path)[:-4]
                year = int(re.search(r"LU\d{4}", cog_id).group()[2:])
                title = f"The {year} AAFC Land Use Maps - {cog_id}"

                self.assertEqual(cog_id, item.id)
                self.assertEqual(title, item.properties["title"])
                self.assertEqual(
                    f"{year}-01-01T00:00:00Z",
                    datetime_to_str(item.common_metadata.start_datetime),
                )

                self.assertIn("metadata", item.assets)

                # Base Projection Extension
                self.assertIn("proj:epsg", item.properties)

                # Base Label Extension
                self.assertIn("label:type", item.properties)
                self.assertIn("label:tasks", item.properties)
                self.assertIn("label:properties", item.properties)
                self.assertIn("label:description", item.properties)
                self.assertIn("label:classes", item.properties)

                item.validate()
