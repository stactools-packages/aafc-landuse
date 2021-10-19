OPEN_CANADA_ID = "fa84a70f-03ad-4946-b0f8-a3b481dd5248"

LANDUSE_ID = f"aafc-landuse-{OPEN_CANADA_ID}"

METADATA_URL = (
    f"https://open.canada.ca/data/api/action/package_show?id={OPEN_CANADA_ID}"
)
PROVIDER_URL = f"https://open.canada.ca/data/en/dataset/{OPEN_CANADA_ID}"
THUMBNAIL_URL = "https://aafc-thumbnails.s3.us-west-2.amazonaws.com/aafc_thumbnail.png"

KEYWORDS = [
    "Land Use",
    "North America",
    "Canada",
    "Remote Sensing",
    "Reflectance",
    "Forest",
    "Water",
    "Wetland",
    "Cropland",
    "Grassland",
    "Settlement",
    "Otherland",
    "AAFC",
    "Open Canada"
]

CLASSIFICATION_VALUES = {
    21: "Settlement: Urban and rural residential, commercial, industrial, transportation or other built infrastructure use",  # noqa
    22: "High Reflectance Settlement: Settlement areas with high spectral reflectance such as pavement, buildings, or other surfaces with little to no observable vegetation",  # noqa
    24: "Settlement Forest: Settlement areas mostly or entirely covered by tree canopy",
    25: "Roads: Primary, secondary and tertiary roads",
    28: "Vegetated Settlement: Settlement areas with observable vegetation such as lawns, golf courses, and settlement areas with 30-50% tree canopy",  # noqa
    29: "Very High Reflectance: Settlement areas with very high spectral reflectance",
    31: "Water: Open water",
    41: "Forest: Land covered by trees with a canopy cover >10% and a minimum height of 5m, or capable of growing to those measurements within 50 years",  # noqa
    42: "Forest Wetland: Wetland with forest cover (canopy cover over 10% and minimum height 5m, or capable of growing to those measurements within 50 years)",  # noqa
    43: "Forest Regenerating after Harvest <20 years: Forest regenerating from tree harvesting activity that took place less than 20 years prior",  # noqa
    44: "Forest Wetland Regenerating after Harvest <20 years: Wetland with forest cover regenerating from tree harvesting activity that took place less than 20 years prior",  # noqa
    49: "Forest Regenerating after Fire <20 years: Forest Regenerating after a fire less than 20 years prior",
    51: "Cropland: Annual and perennial cropland",
    52: "Annual Cropland: Annual cropland (identified beginning in 2015)",
    61: "Grassland Managed: Natural grass and shrubs used for cattle grazing",
    62: "Grassland Unmanaged: Natural grass and shrubs with no discerned human intervention (eg. perpetual meadows, tundra)",  # noqa
    71: "Wetland: Wetland with vegetation at or above the surface of the water",
    91: "Other Land: Rock, beaches, ice, barren land",
}
