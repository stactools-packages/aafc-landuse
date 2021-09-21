import unittest

from pystac.utils import datetime_to_str

from stactools.aafc_landuse import stac, utils


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        metadata = utils.get_metadata()

        # Create stac collection
        collection = stac.create_collection(metadata, 'collection.json')
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

    def test_create_item(self):
        """Create a test item

        :Note: `cog` is an optional parameter and is tested separately in `test_commands`

        """
        metadata = utils.get_metadata()
        metadata["title"] = "IMG_AAFC_LANDUSE_Z07_2010"

        # Create stac item
        item = stac.create_item(metadata, 'item.json')
        item.set_self_href("mock-path")

        self.assertEqual("IMG_AAFC_LANDUSE_Z07_2010", item.id)
        self.assertEqual("IMG_AAFC_LANDUSE_Z07_2010", item.properties["title"])
        self.assertEqual("2010-01-01T00:00:00Z",
                         datetime_to_str(item.common_metadata.start_datetime))

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
