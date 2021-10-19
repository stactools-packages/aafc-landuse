import json
import os
from dateutil.parser import parse
from datetime import datetime, timezone
from types import SimpleNamespace
from pyproj.transformer import Transformer

import requests
import rasterio
from shapely import geometry
from shapely.geometry import mapping as geojson_mapping
from pyproj import CRS


class StacMetadata(SimpleNamespace):
    """AAFC Land Use Stac Metadata namespace"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_datetime(dt_text: str) -> datetime:
        """Parse a string into a datetime in UTC

        Args:
            dt_text (str): Date/time text to parse

        Returns:
            datetime: Datetime object in the UTC timezone
        """
        return parse(dt_text).astimezone(timezone.utc)

    @staticmethod
    def get_bbox(geojson: str) -> list:
        """Parse a goejson string and collect a shapely polygon

        Args:
            geojson (str): Geojson string (can be parsed with loads)

        Returns:
            Polygon: Shapely polygon instance
        """
        return list(geometry.shape(json.loads(geojson)).bounds)


def get_metadata(metadata_path: str) -> StacMetadata:
    """Collect remote metadata published by AAFC

    Args:
        metadata_path (str): Local path or href to metadata json.

    Returns:
        dict: AAFC Land Use Metadata for use in
        `stac.create_collection` and `stac.create_item`
    """
    stac_metadata = StacMetadata()

    if os.path.isfile(metadata_path):
        with open(metadata_path) as f:
            remote_metadata = json.load(f)
    else:
        metadata_response = requests.get(metadata_path)
        remote_metadata = metadata_response.json()["result"]

    stac_metadata.title = remote_metadata["title"]
    stac_metadata.description = remote_metadata["notes"]
    stac_metadata.provider = remote_metadata["organization"]["title"]
    stac_metadata.license_id = remote_metadata["license_id"]
    stac_metadata.license_title = remote_metadata["license_title"]
    stac_metadata.license_url = remote_metadata["license_url"]

    # Temporal extent
    stac_metadata.datetime_start = stac_metadata.get_datetime(
        remote_metadata["time_period_coverage_start"]
    )
    stac_metadata.datetime_end = stac_metadata.get_datetime(
        remote_metadata["time_period_coverage_end"]
    )

    # Bounding box
    stac_metadata.bbox_polygon = stac_metadata.get_bbox(remote_metadata["spatial"])

    # CRS
    stac_metadata.epsg = int(remote_metadata["reference_system_information"][5:10])

    return stac_metadata


def get_raster_metadata(raster_path: str) -> tuple[list, list, list]:
    with rasterio.open(raster_path) as dataset:
        bbox = list(dataset.bounds)
        transform = list(dataset.transform)
        shape = [dataset.height, dataset.width]

    return bbox, transform, shape


def bounds_to_geojson(bbox: list, in_crs: int) -> dict:
    transformer = Transformer.from_crs(
        CRS.from_epsg(in_crs), CRS.from_epsg(4326), always_xy=True
    )
    bbox = list(transformer.transform_bounds(*bbox))
    return geojson_mapping(geometry.box(*bbox, ccw=True))
