from __future__ import annotations

import os
import pandas as pd

from load_data import load_sar_image
from detect_targets import build_water_mask, local_anomaly_detector, blobs_to_points
from match_ais import load_ais_csv, match_detections_to_ais
from make_map import save_final_map


SAR_PATH = "data/raw/sentinel1_vv.tif"
AIS_PATH = "data/ais_mock/ais_mock.csv"

OUT_DETECTIONS = "outputs/detections.geojson"
OUT_MATCHED = "outputs/matched_unmatched.geojson"
OUT_SUMMARY = "outputs/summary.csv"
OUT_MAP = "outputs/final_map.png"


def main():
    os.makedirs("outputs", exist_ok=True)

    print("Loading SAR image...")
    img_db, transform, crs, profile = load_sar_image(SAR_PATH)

    print("Building rough water mask...")
    water_mask = build_water_mask(img_db, db_threshold=-18.0)

    print("Detecting bright local anomalies...")
    anomaly, binary = local_anomaly_detector(
        img_db,
        mask=water_mask,
        win=15,
        offset=6.0,
    )

    print("Converting detections to points...")
    detections_gdf = blobs_to_points(
        binary,
        transform=transform,
        crs=crs,
        min_pixels=3,
        max_pixels=200,
    )

    if detections_gdf.empty:
        print("No detections found. Try adjusting thresholds.")
        return

    print("Saving raw detections...")
    detections_gdf.to_file(OUT_DETECTIONS, driver="GeoJSON")

    print("Loading AIS data...")
    ais_gdf = load_ais_csv(AIS_PATH)

    print("Reprojecting AIS to match SAR CRS...")
    ais_gdf = ais_gdf.to_crs(crs)

    print("Matching detections to AIS...")
    results_gdf = match_detections_to_ais(
        detections_gdf,
        ais_gdf,
        distance_m=500.0,
    )

    print("Saving matched/unmatched detections...")
    results_gdf.to_file(OUT_MATCHED, driver="GeoJSON")

    summary = pd.DataFrame(
        [
            {
                "total_detections": len(results_gdf),
                "matched": int((results_gdf["status"] == "matched").sum()),
                "unmatched": int((results_gdf["status"] == "unmatched").sum()),
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print("Saving final map...")
    save_final_map(
        img_db=img_db,
        detections_gdf=results_gdf,
        ais_gdf=ais_gdf,
        output_path=OUT_MAP,
    )

    print("Done.")
    print(summary)


if __name__ == "__main__":
    main()