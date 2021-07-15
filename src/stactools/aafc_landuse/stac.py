from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import pytz
import logging
from stactools.aafc_landuse.constants import (
    LANDUSE_ID,
    LANDUSE_TITLE,
    DESCRIPTION,
    LANDUSE_PROVIDER,
    LICENSE,
    LICENSE_LINK,
)

import pystac
import rasterio
from rasterio.warp import transform_bounds
from shapely import geometry

logger = logging.getLogger(__name__)


def create_collection(metadata: dict, metadata_url: str) -> pystac.Collection:
    """Create a STAC Collection using a jsonld file provided by AAFC
    and save it to a destination.

    The metadata dict may be created using `utils.get_metadata`

    Args:
        metadata (dict): metadata parsed from jsonld
        metadata_url (str): Location to save the output STAC Collection json

    Returns:
        pystac.Collection: pystac collection object
    """

    dataset_datetime = pytz.utc.localize(datetime.strptime("1990", "%Y"))

    end_datetime = dataset_datetime + relativedelta(years=10)

    start_datetime = dataset_datetime
    end_datetime = end_datetime

    extent_geometry = metadata["geom_metadata"]
    bbox = list(geometry.Polygon(extent_geometry.get("coordinates")[0]).bounds)

    collection = pystac.Collection(
        id=LANDUSE_ID,
        title=LANDUSE_TITLE,
        description=DESCRIPTION,
        providers=[LANDUSE_PROVIDER],
        license=LICENSE,
        extent=pystac.Extent(
            pystac.SpatialExtent([bbox]),
            pystac.TemporalExtent([start_datetime, end_datetime]),
        ),
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
    )
    collection.add_link(LICENSE_LINK)

    collection.set_self_href(metadata_url)

    collection.save_object()

    return collection


def create_item(metadata: dict, metadata_url: str,
                cog_href: str) -> pystac.Item:
    """Creates a STAC item for a 1990, 2000 and 2010 Canada Land Use dataset.

    Args:
        metadata (dict): Contents of the AAFC Land Use jsonld metadata
        metadata_url (str): Output path for the STAC json
        cog_href (str): Location of associated COG asset

    Returns:
        pystac.Item: STAC Item object.
    """

    item_id = ".".join(metadata_url.split(".")[:-1]).split("/")[-1]

    title = item_id
    description = metadata.get("description_metadata").get("dct:description")

    utc = pytz.utc

    year = re.search(r"\d{4}", item_id).group()
    dataset_datetime = utc.localize(datetime.strptime(year, "%Y"))

    end_datetime = dataset_datetime + relativedelta(months=12)

    start_datetime = dataset_datetime
    end_datetime = end_datetime

    src = rasterio.open(cog_href)

    bounds = src.bounds
    bbox = list(transform_bounds(src.crs, "EPSG:4326", *bounds))

    polygon = geometry.box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]

    extent_geometry = {"type": "Polygon", "coordinates": [coordinates]}

    properties = {
        "title": title,
        "description": description,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
    }

    # Create item
    item = pystac.Item(
        id=item_id,
        geometry=extent_geometry,
        bbox=bbox,
        datetime=dataset_datetime,
        properties=properties,
        stac_extensions=[],
    )

    if start_datetime and end_datetime:
        item.common_metadata.start_datetime = start_datetime
        item.common_metadata.end_datetime = end_datetime

    # Create metadata asset
    item.add_asset(
        "json",
        pystac.Asset(
            href=cog_href,
            media_type=pystac.MediaType.JSON,
            roles=["metadata"],
            title="JSON metadata",
        ),
    )

    item.add_asset(
        "cog",
        pystac.Asset(
            href=cog_href,
            media_type=pystac.MediaType.COG,
            roles=["data"],
            title=title,
        ),
    )

    item.set_self_href(metadata_url)

    item.save_object()

    return item
