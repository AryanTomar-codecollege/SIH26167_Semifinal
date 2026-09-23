import React, { useMemo, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import L from "leaflet";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function FitGeoJSON({ data }) {
  const map = useMap();
  if (data?.features?.length) {
    const layer = L.geoJSON(data);
    map.fitBounds(layer.getBounds(), { padding: [24, 24] });
  }
  return null;
}

function App() {
  const [files, setFiles] = useState([]);
  const [query, setQuery] = useState("");
  const [taskHint, setTaskHint] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const geojson = result?.geojson || { type: "FeatureCollection", features: [] };
  const metadata = result?.metadata;
  const trace = result?.execution_trace;

  const fileNames = useMemo(() => files.map((file) => file.name), [files]);

  async function submitQuery(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!files.length || !query.trim()) {
      setError("Choose one or two GeoTIFF files and enter a question.");
      return;
    }

    const form = new FormData();
    files.forEach((file) => form.append("files", file));
    form.append("query", query);
    form.append("task_hint", taskHint);

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/query`, {
        method: "POST",
        body: form,
      });
      const data = await response.json();
      if (!response.ok || data.success === false) {
        throw new Error(data.error || "The backend rejected the request.");
      }
      setResult(data);
    } catch (err) {
      setError(err.message || "Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  function downloadGeoJSON() {
    const blob = new Blob([JSON.stringify(geojson, null, 2)], {
      type: "application/geo+json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "satquery-result.geojson";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">SQ</div>
          <div>
            <div className="brand-name">SatQuery AI</div>
            <div className="brand-subtitle">Remote-sensing assistant · SIH 26167</div>
          </div>
        </div>
        <div className="status-pill"><span /> Backend-ready</div>
      </header>

      <main className="workspace">
        <section className="hero">
          <div>
            <span className="eyebrow">SPACE TECHNOLOGY</span>
            <h1>Ask questions about satellite imagery.</h1>
            <p>
              Upload one image, a temporal pair, or a future optical–SAR pair. The
              backend validates the imagery, routes the request, and returns evidence
              that can be placed on a map.
            </p>
          </div>
          <div className="hero-note">
            <strong>Current build</strong>
            <span>EarthDial is intentionally not connected yet.</span>
          </div>
        </section>

        <div className="grid">
          <section className="panel query-panel">
            <div className="panel-heading">
              <div>
                <h2>New analysis</h2>
                <p>Start with a GeoTIFF and a natural-language question.</p>
              </div>
              <span className="step-badge">01</span>
            </div>

            <form onSubmit={submitQuery}>
              <label className="field-label">Satellite image</label>
              <label className="dropzone">
                <input
                  type="file"
                  accept=".tif,.tiff"
                  multiple
                  onChange={(e) => setFiles(Array.from(e.target.files || []).slice(0, 2))}
                />
                <div className="upload-icon">↑</div>
                <strong>Choose 1–2 GeoTIFF files</strong>
                <span>Maximum two files for single-image or pair analysis.</span>
              </label>

              {fileNames.length > 0 && (
                <div className="file-list">
                  {fileNames.map((name) => <div key={name} className="file-row">▣ {name}</div>)}
                </div>
              )}

              <label className="field-label" htmlFor="query">Question</label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Example: Where are the built-up areas?"
                rows={5}
              />

              <div className="form-row">
                <div className="field-block">
                  <label className="field-label" htmlFor="hint">Task hint</label>
                  <select id="hint" value={taskHint} onChange={(e) => setTaskHint(e.target.value)}>
                    <option value="auto">Auto</option>
                    <option value="vqa">VQA</option>
                    <option value="grounding">Grounding</option>
                    <option value="change">Change detection</option>
                    <option value="optical_sar">Optical + SAR</option>
                  </select>
                </div>
                <button className="run-button" type="submit" disabled={loading}>
                  {loading ? "Running…" : "Run analysis →"}
                </button>
              </div>
            </form>

            {error && <div className="error-box">{error}</div>}
          </section>

          <section className="panel map-panel">
            <div className="panel-heading">
              <div>
                <h2>Evidence map</h2>
                <p>GeoJSON returned by the backend appears here.</p>
              </div>
              <span className="step-badge">02</span>
            </div>
            <div className="map-wrap">
              <MapContainer center={[28.6139, 77.209]} zoom={5} scrollWheelZoom className="map">
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {geojson.features.length > 0 && <GeoJSON data={geojson} />}
                {geojson.features.length > 0 && <FitGeoJSON data={geojson} />}
              </MapContainer>
              {geojson.features.length === 0 && (
                <div className="map-empty">
                  <div className="map-pin">⌖</div>
                  <strong>No geographic evidence yet</strong>
                  <span>Run an analysis to place returned features here.</span>
                </div>
              )}
            </div>
          </section>
        </div>

        <section className="panel result-panel">
          <div className="panel-heading">
            <div>
              <h2>Answer & execution trace</h2>
              <p>The same structured response is designed for the frontend team.</p>
            </div>
            <span className="step-badge">03</span>
          </div>

          {!result ? (
            <div className="empty-result">Your answer will appear here after the first successful request.</div>
          ) : (
            <div className="result-grid">
              <div className="answer-card">
                <span className="mini-label">ANSWER</span>
                <p>{result.answer}</p>
                <div className="confidence">
                  <span>Confidence</span>
                  <strong>{Math.round((result.confidence || 0) * 100)}%</strong>
                </div>
              </div>
              <div className="trace-card">
                <span className="mini-label">EXECUTION TRACE</span>
                <div className="trace-line"><span>Selected task</span><strong>{trace?.selected_task}</strong></div>
                <div className="trace-line"><span>Tool</span><strong>{trace?.tools_used?.join(", ") || "—"}</strong></div>
                <div className="trace-line"><span>Model</span><strong>{trace?.model_used}</strong></div>
                <div className="trace-line"><span>Images</span><strong>{metadata?.num_images}</strong></div>
                <div className="trace-line"><span>CRS</span><strong>{metadata?.crs}</strong></div>
              </div>
            </div>
          )}

          {result && (
            <div className="result-actions">
              <button className="secondary-button" onClick={downloadGeoJSON}>Download GeoJSON</button>
              <span>Backend: {API_URL}</span>
            </div>
          )}
        </section>
      </main>

      <footer>SatQuery AI · SIH 26167 · Student prototype</footer>
    </div>
  );
}

export default App;
