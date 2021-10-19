import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, List, Optional

import fsspec
import pystac
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import (LabelClasses, LabelExtension, LabelTask,
                                     LabelType)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (DataType, RasterBand, RasterExtension,
                                      Sampling)
from pystac.link import Link
from pystac.provider import Provider, ProviderRole
from stactools.core.io import ReadHrefModifier

from stactools.aafc_landuse.constants import (CLASSIFICATION_VALUES, KEYWORDS,
                                              LANDUSE_ID, METADATA_URL,
                                              PROVIDER_URL, THUMBNAIL_URL)
from stactools.aafc_landuse.utils import (bounds_to_geojson, get_metadata,
                                          get_raster_metadata)

logger = logging.getLogger(__name__)


def create_collection(metadata_url: str = METADATA_URL,
                      thumbnail_url: str = THUMBNAIL_URL) -> pystac.Collection:
    """Create a STAC Collection using AAFC Land Use metadata

    Args:
        metadata_url (str, optional): Metadata json provided by AAFC

    Returns:
        pystac.Collection: pystac collection object
    """
    metadata = get_metadata(metadata_url)

    provider = Provider(
        name=metadata.provider,
        roles=[
            ProviderRole.HOST,
            ProviderRole.LICENSOR,
            ProviderRole.PROCESSOR,
            ProviderRole.PRODUCER,
        ],
        url=PROVIDER_URL,
    )

    extent = pystac.Extent(
        pystac.SpatialExtent([metadata.bbox_polygon]),
        pystac.TemporalExtent(
            [[metadata.datetime_start, metadata.datetime_end]]),
    )

    collection = pystac.Collection(
        id=LANDUSE_ID,
        title=metadata.title,
        description=metadata.description,
        providers=[provider],
        license=metadata.license_id,
        extent=extent,
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
        keywords=KEYWORDS,
    )

    collection.add_link(
        Link(rel="license",
             target=metadata.license_url,
             title=metadata.license_title))

    # Add the metadata url and thumbnail url as assets
    collection.add_asset(
        "metadata",
        pystac.Asset(
            href=metadata_url,
            media_type=pystac.MediaType.JSON,
            roles=["metadata"],
            title="AAFC Land Use collection metadata",
        ),
    )
    collection.add_asset(
        "thumbnail",
        pystac.Asset(
            href=thumbnail_url,
            media_type=pystac.MediaType.PNG,
            roles=["thumbnail"],
            title="AAFC Land Use collection thumbnail",
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
    collection_proj.epsg = [metadata.epsg]

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
                    nodata=0,
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
            metadata.epsg,
        }),
    }

    return collection


def create_item(
        cog_href: str,
        metadata_url: str = METADATA_URL,
        cog_href_modifier: Optional[ReadHrefModifier] = None) -> pystac.Item:
    """Creates a STAC item for land use tiles that have been converted to COGs

    Args:
        cog_href (str): Location of associated COG asset
        metadata_url (str, optional): URL for AAFC Land Use metadata json

    Returns:
        pystac.Item: STAC Item object.
    """
    metadata = get_metadata(metadata_url)
    bbox, transform, shape = get_raster_metadata(
        cog_href_modifier(cog_href) if cog_href_modifier else cog_href)
    extent_geometry = bounds_to_geojson(bbox, metadata.epsg)

    # Ensure a year can be retrieved from the path
    cog_id = os.path.basename(cog_href)[:-4]
    match = re.search(r"LU\d{4}", cog_id)
    if not match:
        raise ValueError(
            "The source .tif should originate from a cog created using a source AAFC "
            + "Land Use GeoTiff")
    year = int(match.group()[2:])
    datetime_start = datetime(year, 1, 1, tzinfo=timezone.utc)
    datetime_end = datetime(year, 12, 31, tzinfo=timezone.utc)

    properties = {
        "title": f"The {year} AAFC Land Use Maps - {cog_id}",
        "description": metadata.description,
    }

    # Create item
    item = pystac.Item(
        id=cog_id,
        geometry=extent_geometry,
        bbox=bbox,
        datetime=datetime_start,
        properties=properties,
        stac_extensions=[],
    )

    item.common_metadata.start_datetime = datetime_start
    item.common_metadata.end_datetime = datetime_end

    # Add projection extension
    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = metadata.epsg

    item_projection.bbox = bbox
    item_projection.transform = transform
    item_projection.shape = shape

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
            title="AAFC Land Use metadata source",
        ),
    )

    # COG Asset and extensions
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
    with fsspec.open(
            cog_href_modifier(cog_href) if cog_href_modifier else cog_href
    ) as file:
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
