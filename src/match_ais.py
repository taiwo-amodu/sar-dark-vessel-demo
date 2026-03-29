from __future__ import annotations

import pandas as pd
import geopandas as gpd


def load_ais_csv(path: str) -> gpd.GeoDataFrame:
    """
    Load mock AIS CSV with lon/lat columns.
    """
    df = pd.read_csv(path)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )
    return gdf


def match_detections_to_ais(
    detections_gdf: gpd.GeoDataFrame,
    ais_gdf: gpd.GeoDataFrame,
    distance_m: float = 500.0,
) -> gpd.GeoDataFrame:
    """
    Label detections as matched/unmatched based on nearest AIS point.
    """
    if detections_gdf.empty:
        out = detections_gdf.copy()
        out["status"] = []
        out["nearest_ais_m"] = []
        return out

    det = detections_gdf.to_crs("EPSG:3857").copy()
    ais = ais_gdf.to_crs("EPSG:3857").copy()

    statuses = []
    nearest_distances = []

    for _, det_row in det.iterrows():
        if ais.empty:
            nearest = None
            status = "unmatched"
        else:
            dists = ais.distance(det_row.geometry)
            nearest = float(dists.min())
            status = "matched" if nearest <= distance_m else "unmatched"

        statuses.append(status)
        nearest_distances.append(nearest)

    det["status"] = statuses
    det["nearest_ais_m"] = nearest_distances

    return det