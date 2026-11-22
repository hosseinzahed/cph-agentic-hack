---
name: leaflet-map
description: Recipes for adding layers to the shared Leaflet/OpenStreetMap map of the CPH app - GeoJSON routes, great-circle lines, markers with popups, disruption circles, colour scales and legends - using only theme.css variables. Use when drawing anything on the map in src/frontend/tracks/*.js.
---

# Leaflet map recipes

The map is created once in `src/frontend/app.js`. Tracks draw on it from
`src/frontend/tracks/<track>.js`. Copy what you need from [`snippets.js`](./snippets.js)
(a bundled asset in this skill folder) into your track file.

## Ground rules
- `import { api, getMap, addLayer, clearLayer, cssVar, escapeHtml } from "../app.js";`
- One map only: `getMap()`. One **named layer per concern**: `addLayer("flights:routes", layer)`
  replaces any previous layer with the same name, so `render()` can run many times.
- **Colours only from `theme.css`** through `cssVar("--...")`. Never hard-code hex values.
  - Routes: `--map-route` (Horizon Blue). CPH marker: `--map-cph-fill` + ring `--map-cph-ring`.
  - Other airports: `--map-airport`. Status: `--status-ok`, `--status-warn`, `--status-critical`, `--status-info`.
- Always add a **legend with text labels** for colour-coded layers.
- Escape text in popups and tooltips with `escapeHtml()`.
- Coordinates in Leaflet are `[lat, lon]`; in GeoJSON they are `[lon, lat]`.

## Recipes (see snippets.js)

| Need | Function in snippets.js | Notes |
|---|---|---|
| Routes from a GeoJSON FeatureCollection | `drawRoutes(featureCollection)` | Styles each LineString by `feature.properties.status`. |
| Smooth long-haul routes | `greatCircle([lat1, lon1], [lat2, lon2], 64)` | Returns points along the great circle; split at the antimeridian with `splitAtAntimeridian`. |
| Airport/flight markers with popups | `drawMarkers(items)` | `L.circleMarker` with theme colours and escaped popup text. |
| Disruption circles | `drawDisruptions(disruptions)` | `L.circle(radius_km * 1000)` coloured by severity. |
| Colour scale | `statusColour(status)` / `severityColour(severity)` | Maps values to `--status-*` variables. |
| Legend | `addLegend(name, entries)` | Leaflet control with `.legend` class, colour + text. |
| Does a route cross a circle? | `routeCrossesCircle(points, circle)` | Haversine distance from sampled route points to the centre. |

## Steps
1. Implement (or check) the API endpoint first; test it at http://localhost:8000/docs.
2. In your track's `render(panel)`, `await api(...)` the data. If it throws with
   `error.status === 501`, keep the placeholder.
3. Copy the snippet(s), adapt property names to your response model, and call `addLayer`.
4. Add a legend. Check keyboard access to popups and that there are no console errors.
5. Remove the matching `HACK(<track>)` marker once the layer works.
