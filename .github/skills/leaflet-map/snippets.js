// Leaflet snippets for the CPH Agentic Hack (bundled asset of the leaflet-map skill).
// Copy the functions you need into src/frontend/tracks/<track>.js. They use only theme.css
// variables (via cssVar) and the helpers exported by src/frontend/app.js.

import { addLayer, cssVar, escapeHtml } from "../app.js";

// ---------------------------------------------------------------- colour scales

/** Map a flight/bag status to a theme status colour variable. */
export function statusColour(status) {
  const map = {
    SCHEDULED: "--status-info", BOARDING: "--status-ok", DEPARTED: "--status-ok", LANDED: "--status-ok",
    ON_TIME: "--status-ok", DELAYED: "--status-warn", AT_RISK: "--status-warn",
    CANCELLED: "--status-critical", MISSED: "--status-critical",
  };
  return cssVar(map[status] || "--map-route");
}

/** Map a disruption severity (1-5) to a theme status colour. */
export function severityColour(severity) {
  if (severity >= 4) return cssVar("--status-critical");
  if (severity >= 3) return cssVar("--status-warn");
  return cssVar("--status-info");
}

// ---------------------------------------------------------------- geometry

const toRad = (d) => (d * Math.PI) / 180;
const toDeg = (r) => (r * 180) / Math.PI;

/** Points along the great circle between two [lat, lon] points (inclusive). */
export function greatCircle([lat1, lon1], [lat2, lon2], steps = 64) {
  const φ1 = toRad(lat1), λ1 = toRad(lon1), φ2 = toRad(lat2), λ2 = toRad(lon2);
  const d = 2 * Math.asin(Math.sqrt(Math.sin((φ2 - φ1) / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin((λ2 - λ1) / 2) ** 2));
  if (d === 0) return [[lat1, lon1]];
  const points = [];
  for (let i = 0; i <= steps; i++) {
    const f = i / steps;
    const a = Math.sin((1 - f) * d) / Math.sin(d);
    const b = Math.sin(f * d) / Math.sin(d);
    const x = a * Math.cos(φ1) * Math.cos(λ1) + b * Math.cos(φ2) * Math.cos(λ2);
    const y = a * Math.cos(φ1) * Math.sin(λ1) + b * Math.cos(φ2) * Math.sin(λ2);
    const z = a * Math.sin(φ1) + b * Math.sin(φ2);
    points.push([toDeg(Math.atan2(z, Math.sqrt(x * x + y * y))), toDeg(Math.atan2(y, x))]);
  }
  return points;
}

/** Split a [lat, lon] polyline where it jumps across the antimeridian (for routes like CPH-HND). */
export function splitAtAntimeridian(points) {
  const segments = [[points[0]]];
  for (let i = 1; i < points.length; i++) {
    if (Math.abs(points[i][1] - points[i - 1][1]) > 180) segments.push([]);
    segments.at(-1).push(points[i]);
  }
  return segments;
}

/** Great-circle distance in km between two [lat, lon] points. */
export function haversineKm([lat1, lon1], [lat2, lon2]) {
  const dφ = toRad(lat2 - lat1), dλ = toRad(lon2 - lon1);
  const h = Math.sin(dφ / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dλ / 2) ** 2;
  return 2 * 6371 * Math.asin(Math.sqrt(h));
}

/** True if any sampled route point lies inside the disruption circle. */
export function routeCrossesCircle(points, { lat, lon, radius_km }) {
  return points.some((p) => haversineKm(p, [lat, lon]) <= radius_km);
}

// ---------------------------------------------------------------- layers

/** Draw a GeoJSON FeatureCollection of LineStrings, coloured by properties.status. */
export function drawRoutes(featureCollection, layerName = "flights:routes") {
  const layer = L.geoJSON(featureCollection, {
    style: (feature) => ({ color: statusColour(feature.properties?.status), weight: 2, opacity: 0.8 }),
    onEachFeature: (feature, line) => {
      const p = feature.properties || {};
      line.bindTooltip(`${escapeHtml(p.flight_no ?? "")} ${escapeHtml(p.dest_iata ?? "")} · ${escapeHtml(p.status ?? "")}`);
    },
  });
  return addLayer(layerName, layer);
}

/** Draw great-circle polylines from CPH to each destination ({ lat, lon, label, status }). */
export function drawGreatCircleRoutes(destinations, cph = [55.618, 12.656], layerName = "flights:routes") {
  const lines = destinations.flatMap((d) =>
    splitAtAntimeridian(greatCircle(cph, [d.lat, d.lon])).map((segment) =>
      L.polyline(segment, { color: statusColour(d.status), weight: 2, opacity: 0.8 }).bindTooltip(escapeHtml(d.label)),
    ),
  );
  return addLayer(layerName, L.layerGroup(lines));
}

/** Draw circle markers with escaped popups. items: [{ lat, lon, title, text, status }] */
export function drawMarkers(items, layerName) {
  const markers = items.map((item) =>
    L.circleMarker([item.lat, item.lon], {
      radius: 6, weight: 1, color: cssVar("--cph-white"),
      fillColor: item.status ? statusColour(item.status) : cssVar("--map-airport"), fillOpacity: 0.9,
    }).bindPopup(`<strong>${escapeHtml(item.title)}</strong><br>${escapeHtml(item.text ?? "")}`),
  );
  return addLayer(layerName, L.layerGroup(markers));
}

/** Draw disruption circles: [{ lat, lon, radius_km, severity, title, type }] */
export function drawDisruptions(disruptions, layerName = "disruptions:circles") {
  const circles = disruptions.map((d) =>
    L.circle([d.lat, d.lon], {
      radius: d.radius_km * 1000, color: severityColour(d.severity), weight: 2,
      fillColor: severityColour(d.severity), fillOpacity: 0.2,
    }).bindPopup(`<strong>${escapeHtml(d.title)}</strong><br>${escapeHtml(d.type)} · severity ${escapeHtml(d.severity)}/5`),
  );
  return addLayer(layerName, L.layerGroup(circles));
}

/** Add a legend control. entries: [{ colour: cssVar(...), label: "Delayed" }] */
export function addLegend(layerName, entries, position = "bottomright") {
  const legend = L.control({ position });
  legend.onAdd = () => {
    const div = L.DomUtil.create("div", "legend");
    for (const { colour, label } of entries) {
      const row = document.createElement("div");
      const swatch = document.createElement("span");
      swatch.setAttribute("aria-hidden", "true");
      swatch.style.cssText = `display:inline-block;width:0.8em;height:0.8em;margin-right:0.4em;border-radius:50%;background:${colour}`;
      row.append(swatch, document.createTextNode(label));
      div.append(row);
    }
    return div;
  };
  return addLayer(layerName, legend);
}
