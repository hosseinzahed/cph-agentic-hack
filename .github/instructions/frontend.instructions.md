---
applyTo: "src/frontend/**"
description: "Vanilla JS, Leaflet, Chart.js and CPH-inspired theme rules for the CPH Agentic Hack UI."
---

# Frontend conventions

## No build tooling
- Plain HTML, CSS and JavaScript **ES modules** (`<script type="module">`). No npm, bundler,
  TypeScript, React or other framework.
- Leaflet 1.9.4 and Chart.js 4.6.1 come from the CDN in `index.html` (pinned versions with SRI).
  Use the globals `L` and `Chart`. Don't add more libraries unless your track guide suggests one.

## Modules and helpers
- Each track owns one file, `src/frontend/tracks/<track>.js`, exporting `render(panel)`; it is
  called whenever its tab is shown, so make it safe to call repeatedly.
- Reuse the helpers exported by `src/frontend/app.js`:
  - `api(path, options)`: fetch JSON; throws an Error with `.status` and `.detail` (a 501 stub
    throws with `status === 501`, so you can keep showing the placeholder).
  - `addLayer(name, layer)` / `clearLayer(name)`: named map layers. Prefix names with your track,
    e.g. `"flights:routes"`, so tracks don't overwrite each other.
  - `renderPlaceholder(el, track, hint)`, `getMap()`, `cssVar(name)`, `chartPalette()`, `escapeHtml(text)`.
- Import helpers with `import { api, addLayer } from "../app.js";`. Exported helpers are function
  declarations, so they are safe to import from track modules.

## Leaflet
- One shared map (`getMap()`), centred on CPH (55.618, 12.656). Never create a second map.
- Keep each visual concern in its own named layer; clear it before redrawing.
- Colours come from CSS variables: routes `--map-route`, airports `--map-airport`, CPH marker
  `--map-cph-fill` with ring `--map-cph-ring`, disruptions `--status-*` with low fill opacity.
- Escape any text you put in popups with `escapeHtml()`.
- Keep the "© OpenStreetMap contributors" attribution. OSM tiles are fine for the workshop only.

## Chart.js
- Defaults (font, text colour, grid lines) are set once in `app.js` from `theme.css`. Don't
  override them per chart; pick series colours from `chartPalette()` or `cssVar(...)`.
- Destroy an existing chart before re-creating it on the same canvas (`chart.destroy()`).
- Give every `<canvas>` an `aria-label` or a visible caption, and provide a table/text alternative
  for the key numbers.

## CPH-inspired theme rules
- **Use only `theme.css` variables for colours and fonts. Never hard-code hex values in components.**
  `theme.css` is the only file with colour values.
- Patterns: Midnight Blue header with a Sunrise Yellow accent; rounded white cards (`.card`);
  KPI tiles (`.kpi`); pill/underline tabs; primary buttons `.btn--primary` (Sunrise Yellow,
  Midnight Blue text) and secondary `.btn--secondary` (Horizon Blue outline); flight board
  `.board`; chat bubbles `.msg--user` / `.msg--assistant`.
- Status colours: `--status-ok`, `--status-warn`, `--status-critical`, `--status-info`, shown with
  `.chip--ok/warn/critical/info`. **Always include a text label or icon** with a status colour.
- Text is left-aligned everywhere. Body text 16px or more. Use `font-variant-numeric: tabular-nums`
  (class `.tabular`) for times, flight numbers and counts.
- Show times in Europe/Copenhagen: `new Date(iso).toLocaleTimeString("en-GB", { timeZone: "Europe/Copenhagen", hour: "2-digit", minute: "2-digit" })`.

## Accessibility
- Keep landmarks, the keyboard-navigable tabs and visible focus states working.
- Insert untrusted or model-generated text with `textContent`, never `innerHTML`.
- See `a11y.instructions.md` for the full WCAG 2.2 AA guidance.
