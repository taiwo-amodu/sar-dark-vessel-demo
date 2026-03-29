from __future__ import annotations

import numpy as np
import rasterio


def load_sar_image(path: str):
    """
    Load a SAR GeoTIFF and convert to dB scale.
    Assumes image is already georeferenced.
    """
    with rasterio.open(path) as src:
        img = src.read(1).astype("float32")
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs

    # Avoid invalid log values
    img = np.where(img <= 0, np.nan, img)

    # Convert to dB
    img_db = 10.0 * np.log10(img)

    return img_db, transform, crs, profile