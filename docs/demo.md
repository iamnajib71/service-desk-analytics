# Demo recording

`docs/demo.gif` is a real browser capture of the running synthetic dashboard, recorded with Playwright at one frame per second and encoded with Pillow. It shows the local working application: overview, an opening-cohort change, ageing/demand views, repeat-work/CSAT views and evidence export. It is not a rendered slide animation or a mock dashboard.

The full application is also available as local Streamlit and a synthetic-only static Plotly deployment. `docs/img/streamlit-overview.png` is captured from Streamlit; the detail screenshot is captured from the Pages version of the same shared charts.

To reproduce the capture, run Streamlit on port 8501 and serve `site` on port 8000, then use `scripts/capture_demo.cjs` with Playwright installed. `scripts/make_media.py` encodes the recorded PNG frames as the GIF and generates the 1280×640 social preview. Capture tooling is optional and not part of the warehouse rebuild. Browser animations are sampled for the GIF, so motion is less smooth than the live application.

Nazmul can upload `docs/social-preview.png` under GitHub repository Settings → General → Social preview. GitHub CLI has no repository social-preview upload endpoint.
