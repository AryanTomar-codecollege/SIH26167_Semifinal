from __future__ import annotations

from pathlib import Path
from typing import Any

import rasterio
from rasterio.warp import transform_bounds
from shapely.geometry import box, mapping


def extract_metadata(filepath: str) -> dict[str, Any]:
    """Read core spatial metadata from a GeoTIFF."""
    with rasterio.open(filepath) as dataset:
        if dataset.crs is None:
            raise ValueError("GeoTIFF does not contain a CRS.")

        bounds = dataset.bounds
        bounds_4326 = transform_bounds(
            dataset.crs,
            "EPSG:4326",
            bounds.left,
            bounds.bottom,
            bounds.right,
            bounds.top,
        )

        return {
            "crs": dataset.crs.to_string(),
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "transform": list(dataset.transform)[:6],
            "bounds_native": {
                "left": bounds.left,
                "bottom": bounds.bottom,
                "right": bounds.right,
                "top": bounds.top,
            },
            "bounds_4326": {
                "west": bounds_4326[0],
                "south": bounds_4326[1],
                "east": bounds_4326[2],
                "north": bounds_4326[3],
            },
        }


def pixel_box_to_geojson(filepath: str, pixel_box: list[float]) -> dict[str, Any]:
    """Convert [x1, y1, x2, y2] pixel coordinates to a GeoJSON polygon."""
    if len(pixel_box) != 4:
        raise ValueError("pixel_box must contain [x1, y1, x2, y2].")

    with rasterio.open(filepath) as dataset:
        if dataset.crs is None:
            raise ValueError("GeoTIFF does not contain a CRS.")

        x1, y1, x2, y2 = pixel_box
        x1, x2 = sorted((float(x1), float(x2)))
        y1, y2 = sorted((float(y1), float(y2)))

        # Rasterio's affine transform maps pixel coordinates to native CRS.
        left, top = dataset.transform * (x1, y1)
        right, bottom = dataset.transform * (x2, y2)

        native_polygon = box(left, bottom, right, top)

        # Convert the polygon corners to EPSG:4326 without introducing a
        # second geometry library just for this simple rectangle.
        from rasterio.warp import transform_geom

        geojson_geometry = transform_geom(
            dataset.crs,
            "EPSG:4326",
            mapping(native_polygon),
        )

        return {
            "type": "Feature",
            "properties": {},
            "geometry": geojson_geometry,
        }


def images_overlap(filepath_a: str, filepath_b: str) -> bool:
    """Return whether two GeoTIFF footprints intersect in EPSG:4326."""
    with rasterio.open(filepath_a) as a, rasterio.open(filepath_b) as b:
        if a.crs is None or b.crs is None:
            raise ValueError("Both GeoTIFFs must contain a CRS.")

        a_bounds = transform_bounds(a.crs, "EPSG:4326", *a.bounds)
        b_bounds = transform_bounds(b.crs, "EPSG:4326", *b.bounds)

    a_box = box(a_bounds[0], a_bounds[1], a_bounds[2], a_bounds[3])
    b_box = box(b_bounds[0], b_bounds[1], b_bounds[2], b_bounds[3])
    return a_box.intersects(b_box)


def validate_geotiff_path(filepath: str) -> None:
    """Fail early if the uploaded file is not a readable GeoTIFF."""
    path = Path(filepath)
    if path.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError("Only GeoTIFF files (.tif or .tiff) are supported.")

    try:
        with rasterio.open(path) as dataset:
            if dataset.crs is None:
                raise ValueError("GeoTIFF does not contain a CRS.")
    except rasterio.errors.RasterioIOError as exc:
        raise ValueError("The uploaded file is not a readable GeoTIFF.") from exc
