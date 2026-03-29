# Maritime Anomaly Detection from Sentinel-1 SAR

## Overview
This project demonstrates a simple geospatial workflow for detecting vessel-like targets in SAR imagery and flagging detections without matching AIS reports as possible maritime anomalies.

## Objective
Simulate a dark-vessel screening workflow using:
- Sentinel-1 SAR imagery
- Python geospatial processing
- AIS-like vessel position data

## Workflow
1. Load Sentinel-1 SAR GeoTIFF
2. Convert to dB scale
3. Build a rough water mask
4. Detect bright local anomalies over water
5. Convert detection blobs to point features
6. Load mock AIS data
7. Match SAR detections to AIS points
8. Flag unmatched detections

## Tools
- Python
- Rasterio
- NumPy
- GeoPandas
- SciPy
- Matplotlib

## Outputs
- `detections.geojson` — all detected vessel-like targets
- `matched_unmatched.geojson` — detections labeled as matched/unmatched
- `summary.csv` — summary statistics
- `final_map.png` — analyst-style quicklook image

## Notes
This is a demonstration workflow, not a production maritime surveillance system.

## Limitations
- Uses a simple local anomaly detector rather than full CFAR
- AIS is simulated for demonstration purposes
- No wake analysis or temporal confirmation
- False positives may occur from infrastructure, sea clutter, or bright non-vessel targets
