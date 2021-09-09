import json
import os
import shutil
from tempfile import gettempdir
from typing import Any
from uuid import uuid1
from zipfile import ZipFile

import requests


def get_metadata(metadata_url: str) -> dict:
    """Gets metadata from a jsonld published by AAFC
    Args:
        metadata_url (str): url to get metadata from.
    Returns:
        dict: AAFC Land Use Metadata.
    """
    if metadata_url.endswith(".jsonld"):
        if metadata_url.startswith("http"):
            metadata_response = requests.get(metadata_url)
            jsonld_response = metadata_response.json()
        else:
            with open(metadata_url) as f:
                jsonld_response = json.load(f)

        geom_obj = next(
            (x["locn:geometry"] for x in jsonld_response["@graph"]
             if "locn:geometry" in x.keys()),
            [],
        )  # type: Any
        geom_metadata = next(
            (json.loads(x["@value"])
             for x in geom_obj if x["@type"].startswith("http")),
            None,
        )
        if not geom_metadata:
            raise ValueError("Unable to parse geometry metadata from jsonld")

        description_metadata = [
            i for i in jsonld_response.get("@graph")
            if "dct:description" in i.keys()
        ][0]

        metadata = {
            "geom_metadata": geom_metadata,
            "description_metadata": description_metadata,
        }

        return metadata
    else:
        # only jsonld support.
        raise NotImplementedError()


class AssetManager:
    """Manage an asset as a local file, or temporary local file if a url is provided
    """
    def __init__(self, src: str):
        if os.path.splitext(src)[1].lower() not in [".tif", ".zip"]:
            raise ValueError("Asset is expected to be .tif or .zip")

        # Create a temporary working directory
        self.src = src
        self.wkdir = os.path.join(gettempdir(), str(uuid1()))
        os.mkdir(self.wkdir)

        if os.path.isfile(src):
            self.path = self.extract_and_find(self.src)
        else:
            dl_path = self.collect_remote_asset()
            self.path = self.extract_and_find(dl_path)

    def collect_remote_asset(self):
        """Download the asset
        """
        # Download the asset
        dl = os.path.join(self.wkdir, os.path.basename(self.src))
        with open(dl, "wb") as af:
            af.write(requests.get(self.src).content)

        return dl

    def extract_and_find(self, src: str):
        """Extract an asset if needed and traverse to find the first .tif

        Args:
            src (str): Path to the asset

        Returns:
            str: Path to the first .tif encountered
        """
        if os.path.splitext(src)[1].lower() == ".zip":
            with ZipFile(src, "r") as zf:
                zf.extractall(self.wkdir)

            for p, _, contents in os.walk(self.wkdir):
                for c in contents:
                    if os.path.splitext(c)[1].lower() == ".tif":
                        return os.path.join(p, c)

            raise FileNotFoundError("No .tif files in asset source")
        else:
            return src

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        try:
            shutil.rmtree(self.wkdir)
        except FileNotFoundError:
            pass
