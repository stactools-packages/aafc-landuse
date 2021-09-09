import unittest

from stactools.aafc_landuse.constants import JSONLD_HREF
from stactools.aafc_landuse import utils
from stactools.aafc_landuse import stac


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        metadata = utils.get_metadata(JSONLD_HREF)

        # Create stac collection
        collection = stac.create_collection(metadata)
        collection.set_self_href('mock-path')

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
        metadata = utils.get_metadata(JSONLD_HREF)

        # Create stac item
        item = stac.create_item(metadata, JSONLD_HREF)
        item.set_self_href('mock-path')

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
