ARG STACTOOLS_VERSION=latest
FROM stacutils/stactools:$STACTOOLS_VERSION

WORKDIR /opt/stactools-aafc-landuse

# For caching purposes, install dependencies but remove the actual package
COPY pyproject.toml setup.cfg ./
COPY src/stactools/aafc_landuse/__init__.py src/stactools/aafc_landuse/
RUN pip install . \
    && rm -r /opt/conda/lib/python3.8/site-packages/stactools/aafc_landuse

COPY src ./src
RUN pip install .
