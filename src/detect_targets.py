from __future__ import annotations

import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import xy
from scipy.ndimage import uniform_filter, label, find_objects
from shapely.geometry import Point


def build_water_mask(img_db: np.ndarray, db_threshold: float = -18.0) -> np.ndarray:
    """
    Very rough water mask.
    Assumes darker pixels are more likely water.
    You may need to tune this threshold per scene.
    """
    mask = np.isfinite(img_db) & (img_db < db_threshold)
    return mask


def local_anomaly_detector(
    img_db: np.ndarray,
    mask: np.ndarray | None = None,
    win: int = 15,
    offset: float = 6.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Detect bright local anomalies against local background.
    """
    work = img_db.copy()

    if mask is not None:
        work = np.where(mask, work, np.nan)

    # Fill NaNs for filter computation
    finite_vals = work[np.isfinite(work)]
    if finite_vals.size == 0:
        raise ValueError("No valid pixels found after masking.")

    fill_value = np.nanmedian(finite_vals)
    filled = np.where(np.isfinite(work), work, fill_value)

    local_mean = uniform_filter(filled, size=win)
    anomaly = filled - local_mean

    detections = anomaly > offset

    if mask is not None:
        detections = detections & mask

    return anomaly, detections


def blobs_to_points(
    binary_img: np.ndarray,
    transform,
    crs,
    min_pixels: int = 3,
    max_pixels: int = 200,
) -> gpd.GeoDataFrame:
    """
    Convert connected detection blobs to centroid points.
    """
    labeled, n_labels = label(binary_img)
    slices = find_objects(labeled)

    rows = []
    for label_id, slc in enumerate(slices, start=1):
        if slc is None:
            continue

        rr, cc = np.where(labeled == label_id)
        pixel_count = int(len(rr))

        if pixel_count < min_pixels or pixel_count > max_pixels:
            continue

        r_mean = float(rr.mean())
        c_mean = float(cc.mean())
        x, y = xy(transform, r_mean, c_mean)

        rows.append(
            {
                "det_id": label_id,
                "pixels": pixel_count,
                "geometry": Point(x, y),
            }
        )

    if not rows:
        return gpd.GeoDataFrame(columns=["det_id", "pixels", "geometry"], crs=crs)

    return gpd.GeoDataFrame(rows, crs=crs)