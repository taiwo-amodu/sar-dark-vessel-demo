from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd


def save_final_map(
    img_db: np.ndarray,
    detections_gdf: gpd.GeoDataFrame,
    ais_gdf: gpd.GeoDataFrame,
    output_path: str,
    title: str = "Maritime Anomaly Detection from SAR",
):
    """
    Save a simple analyst-style map.
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.imshow(img_db, cmap="gray")
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])

    if not detections_gdf.empty:
        matched = detections_gdf[detections_gdf["status"] == "matched"]
        unmatched = detections_gdf[detections_gdf["status"] == "unmatched"]

        # These are geographic coordinates, so for a quick plot we assume
        # user will mainly use this as a schematic overlay.
        # Better plotting comes after converting world coords to pixel coords.
        # For now, we just export geospatial results and use this figure as a quicklook.

        ax.text(
            0.02,
            0.98,
            f"Detections: {len(detections_gdf)}\n"
            f"Matched: {len(matched)}\n"
            f"Unmatched: {len(unmatched)}",
            transform=ax.transAxes,
            va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close(fig)