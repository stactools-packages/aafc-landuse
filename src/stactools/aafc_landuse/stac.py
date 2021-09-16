import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import fsspec
import pystac
import pytz
import rasterio
from dateutil.relativedelta import relativedelta
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import (LabelClasses, LabelExtension, LabelTask,
                                     LabelType)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (DataType, RasterBand, RasterExtension,
                                      Sampling)
from shapely import geometry

from stactools.core.utils.convert import cogify
from stactools.aafc_landuse.constants import (CLASSIFICATION_VALUES,
                                              DESCRIPTION, JSONLD_HREF,
                                              LANDUSE_EPSG, LANDUSE_ID,
                                              LANDUSE_PROVIDER, LANDUSE_TITLE,
                                              LICENSE, LICENSE_LINK)

logger = logging.getLogger(__name__)


def create_collection(metadata: dict,
                      metadata_url: str = JSONLD_HREF) -> pystac.Collection:
    """Create a STAC Collection using a jsonld file provided by AAFC
    and save it to a destination.

    The metadata dict may be created using `utils.get_metadata`

    Args:
        metadata (dict): metadata parsed from jsonld
        metadata_url (str, optional): Location of metadata

    Returns:
        pystac.Collection: pystac collection object
    """

    dataset_datetime = pytz.utc.localize(datetime.strptime("1990", "%Y"))

    end_datetime = dataset_datetime + relativedelta(years=10)

    start_datetime = dataset_datetime  # type: Optional[datetime]
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
            pystac.TemporalExtent([[start_datetime, end_datetime]]),
        ),
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
    )
    collection.add_link(LICENSE_LINK)

    # Add asset
    collection.add_asset(
        "metadata",
        pystac.Asset(
            href=metadata_url,
            media_type=pystac.MediaType.JSON,
            roles=["metadata"],
            title="AAFC Land Use collection metadata",
        ),
    )

    collection_label = LabelExtension.summaries(collection,
                                                add_if_missing=True)
    collection_label.label_type = [LabelType.RASTER]
    collection_label.label_tasks = [LabelTask.CLASSIFICATION]
    collection_label.label_properties = None
    collection_label.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(list(CLASSIFICATION_VALUES.values()), "")
    ]

    collection_proj = ProjectionExtension.summaries(collection,
                                                    add_if_missing=True)
    collection_proj.epsg = [LANDUSE_EPSG]

    collection_item_asset = ItemAssetsExtension.ext(collection,
                                                    add_if_missing=True)
    collection_item_asset.item_assets = {
        "metadata":
        AssetDefinition(
            dict(
                type=pystac.MediaType.JSON,
                roles=["metadata"],
                title="AAFC Land Use metadata",
            )),
        "landuse":
        AssetDefinition({
            "type":
            pystac.MediaType.COG,
            "roles": [
                "data",
                "labels",
                "labels-raster",
            ],
            "title":
            "AAFC Land Use COG",
            "raster:bands": [
                RasterBand.create(
                    nodata=127,
                    sampling=Sampling.AREA,
                    data_type=DataType.UINT8,
                    spatial_resolution=30,
                ).to_dict()
            ],
            "file:values": [{
                "values": [value],
                "summary": summary
            } for value, summary in CLASSIFICATION_VALUES.items()],
            "label:type":
            collection_label.label_type[0],
            "label:tasks":
            collection_label.label_tasks,
            "label:properties":
            None,
            "label:classes": [collection_label.label_classes[0].to_dict()],
            "proj:epsg":
            collection_proj.epsg[0],
        }),
    }

    return collection


def create_item(
    metadata: dict,
    metadata_url: str = JSONLD_HREF,
    cog_href: Optional[str] = None,
) -> pystac.Item:
    """Creates a STAC item for a 1990, 2000 and 2010 Canada Land Use dataset.

    Args:
        metadata (dict): Contents of the AAFC Land Use jsonld metadata
        metadata_url (str, optional): Output path for the STAC metadata json
        cog_href (str, optional): Location of associated COG asset

    Returns:
        pystac.Item: STAC Item object.
    """

    title = metadata.get("title", None)

    if not title:
        raise KeyError('Attribute "title" missing from metadata')

    desc_metadata = metadata["description_metadata"]
    if not isinstance(desc_metadata, dict):
        raise ValueError('Expected a dictionary of description metadata')

    description = desc_metadata.get("dct:description")

    # Parse the year from the title
    match = re.search(r"\d{4}", title)
    if not match:
        raise ValueError("No year found in title")

    year = match.group()
    dataset_datetime = pytz.utc.localize(datetime.strptime(year, "%Y"))

    end_datetime = dataset_datetime + relativedelta(months=12)

    start_datetime = dataset_datetime
    end_datetime = end_datetime

    bbox = list(
        geometry.Polygon(metadata["geom_metadata"]["coordinates"][0]).bounds)

    polygon = geometry.box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]

    extent_geometry = {"type": "Polygon", "coordinates": [coordinates]}

    properties = {"title": title, "description": description}

    # Create item
    item = pystac.Item(
        id=title,
        geometry=extent_geometry,
        bbox=bbox,
        datetime=dataset_datetime,
        properties=properties,
        stac_extensions=[],
    )

    if start_datetime and end_datetime:
        item.common_metadata.start_datetime = start_datetime
        item.common_metadata.end_datetime = end_datetime

    # Add projection extension
    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = LANDUSE_EPSG

    if cog_href is not None:
        with rasterio.open(cog_href) as dataset:
            item_projection.bbox = list(dataset.bounds)
            item_projection.transform = list(dataset.transform)
            item_projection.shape = [dataset.height, dataset.width]

    # Add label extension
    item_label = LabelExtension.ext(item, add_if_missing=True)
    item_label.label_type = LabelType.RASTER
    item_label.label_tasks = [LabelTask.CLASSIFICATION]
    item_label.label_properties = None
    item_label.label_description = ""
    item_label.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(list(CLASSIFICATION_VALUES.values()), "")
    ]

    # Create metadata asset
    item.add_asset(
        "metadata",
        pystac.Asset(
            href=metadata_url,
            media_type=pystac.MediaType.JSON,
            roles=["metadata"],
            title="AAFC Land Use item metadata",
        ),
    )
    if cog_href is not None:
        # Create COG asset if it is provided
        cog_asset = pystac.Asset(
            href=cog_href,
            media_type=pystac.MediaType.COG,
            roles=["data", "labels", "labels-raster"],
            title="AAFC Land Use item COG",
        )
        item.add_asset("landuse", cog_asset)

        # File Extension
        cog_asset_file = FileExtension.ext(cog_asset, add_if_missing=True)
        mapping: List[Any] = [{
            "values": [value],
            "summary": summary
        } for value, summary in CLASSIFICATION_VALUES.items()]
        cog_asset_file.values = mapping
        with fsspec.open(cog_href) as file:
            size = file.size
            if size is not None:
                cog_asset_file.size = size

        # Raster Extension
        cog_asset_raster = RasterExtension.ext(cog_asset, add_if_missing=True)
        cog_asset_raster.bands = [
            RasterBand.create(
                nodata=0,
                sampling=Sampling.AREA,
                data_type=DataType.UINT8,
                spatial_resolution=30,
            )
        ]

        # Complete the projection extension
        cog_asset_projection = ProjectionExtension.ext(cog_asset,
                                                       add_if_missing=True)
        cog_asset_projection.epsg = item_projection.epsg
        cog_asset_projection.bbox = item_projection.bbox
        cog_asset_projection.transform = item_projection.transform
        cog_asset_projection.shape = item_projection.shape

    return item
