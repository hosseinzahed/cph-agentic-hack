// app.js: map set-up, tab switching and small helpers that every track reuses.
// Plain ES modules, no build step. Colours always come from theme.css via cssVar().

import { render as renderOnboarding } from "./tracks/onboarding.js";
import { render as renderFlights } from "./tracks/flights.js";
import { render as renderDisruptions } from "./tracks/disruptions.js";
import { render as renderGates } from "./tracks/gates.js";
import { initAssistant } from "./tracks/assistant.js";

const CPH = { lat: 55.618, lon: 12.656 };
const TRACKS = {
  onboarding: renderOnboarding,
  flights: renderFlights,
  disruptions: renderDisruptions,
  gates: renderGates,
};

let map = null;
const layers = new Map(); // layer name -> Leaflet layer

// ---------------------------------------------------------------- helpers (import these)

/** Read a CSS custom property from theme.css, e.g. cssVar("--cph-horizon-blue"). */
export function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

/**
 * Fetch JSON from the backend. Throws an Error with `.status` and `.detail` on HTTP errors,
 * so a 501 stub can be shown as a placeholder.
 */
export async function api(path, options = {}) {
  const init = { ...options, headers: { Accept: "application/json", ...(options.headers || {}) } };
  if (init.body && typeof init.body !== "string") {
    init.body = JSON.stringify(init.body);
    init.headers["Content-Type"] = "application/json";
  }
  const response = await fetch(path, init);
  const data = response.headers.get("content-type")?.includes("json") ? await response.json() : null;
  if (!response.ok) {
    const error = new Error(data?.detail || `${response.status} ${response.statusText}`);
    error.status = response.status;
    error.detail = data?.detail;
    throw error;
  }
  return data;
}

/** The shared Leaflet map (available after the page has loaded). */
export function getMap() {
  return map;
}

/** Add (or replace) a named layer on the map, e.g. addLayer("flights:routes", geoJsonLayer). */
export function addLayer(name, layer) {
  clearLayer(name);
  layers.set(name, layer);
  layer.addTo(map);
  return layer;
}

/** Remove a named layer from the map if it exists. */
export function clearLayer(name) {
  const existing = layers.get(name);
  if (existing) {
    existing.remove();
    layers.delete(name);
  }
}

/** Show the friendly "🚧 HACK(track)" placeholder card inside `el`. */
export function renderPlaceholder(el, track, hint) {
  el.replaceChildren();
  const card = document.createElement("div");
  card.className = "placeholder";
  const title = document.createElement("p");
  title.className = "placeholder__title";
  title.textContent = `🚧 HACK(${track}): ${hint.title}`;
  const body = document.createElement("p");
  body.className = "placeholder__hint";
  body.textContent = hint.text;
  card.append(title, body);
  el.append(card);
}

/** Escape text before putting it into HTML (popups, chat bubbles). Prefer textContent when you can. */
export function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

/** Theme colours for Chart.js series, in order. */
export function chartPalette() {
  return ["--cph-horizon-blue", "--cph-twilight-blue", "--cph-sky-blue", "--cph-sunrise-yellow", "--cph-evening-blue"].map(cssVar);
}

// ---------------------------------------------------------------- map

function initMap() {
  map = L.map("map", { worldCopyJump: true }).setView([CPH.lat, CPH.lon], 4);

  // Standard OSM tiles: fine for a workshop, NOT for production traffic.
  // See the OSM tile usage policy: https://operations.osmfoundation.org/policies/tiles/
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    className: "osm-tiles",
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  }).addTo(map);
}

async function addAirportMarkers() {
  const airports = await api("/api/airports");
  const markers = airports
    .filter((a) => a.iata !== "CPH")
    .map((a) =>
      L.circleMarker([a.lat, a.lon], {
        radius: 5,
        color: cssVar("--cph-white"),
        weight: 1,
        fillColor: cssVar("--map-airport"),
        fillOpacity: 0.9,
      }).bindPopup(`<strong>${escapeHtml(a.iata)}</strong><br>${escapeHtml(a.name)}<br>${escapeHtml(a.city)}, ${escapeHtml(a.country)}`),
    );
  addLayer("airports", L.layerGroup(markers));

  addLayer(
    "cph",
    L.circleMarker([CPH.lat, CPH.lon], {
      radius: 9,
      color: cssVar("--map-cph-ring"),
      weight: 4,
      fillColor: cssVar("--map-cph-fill"),
      fillOpacity: 1,
    }).bindPopup("<strong>CPH</strong><br>Copenhagen Airport Kastrup"),
  );
}

// ---------------------------------------------------------------- Chart.js defaults

function initChartDefaults() {
  if (!window.Chart) return;
  Chart.defaults.font.family = cssVar("--font-sans");
  Chart.defaults.font.size = 14;
  Chart.defaults.color = cssVar("--cph-storm-grey");
  Chart.defaults.borderColor = cssVar("--cph-misty-grey");
  Chart.defaults.backgroundColor = cssVar("--cph-sky-blue");
  Chart.defaults.plugins.legend.align = "start";
}

// ---------------------------------------------------------------- tabs (WAI-ARIA tabs pattern)

function initTabs() {
  const tabs = [...document.querySelectorAll('[role="tab"]')];

  function select(tab) {
    for (const t of tabs) {
      const selected = t === tab;
      t.setAttribute("aria-selected", String(selected));
      t.tabIndex = selected ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !selected;
    }
    const panel = document.getElementById(tab.getAttribute("aria-controls"));
    TRACKS[tab.dataset.track](panel);
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => select(tab));
    tab.addEventListener("keydown", (event) => {
      const moves = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: tabs.length - 1 };
      if (!(event.key in moves)) return;
      event.preventDefault();
      const next = tabs[(moves[event.key] + tabs.length) % tabs.length];
      next.focus();
      select(next);
    });
  });

  select(tabs.find((t) => t.getAttribute("aria-selected") === "true") || tabs[0]);
}

// ---------------------------------------------------------------- health indicator

async function refreshHealth() {
  const el = document.getElementById("health");
  const text = el.querySelector(".health__text");
  try {
    const health = await api("/api/health");
    el.className = `health ${health.db ? "health--ok" : "health--warn"}`;
    text.textContent = health.db ? "API ok · data seeded" : "API ok · run the seed script";
  } catch {
    el.className = "health health--down";
    text.textContent = "API not reachable";
  }
}

// ---------------------------------------------------------------- start

document.addEventListener("DOMContentLoaded", () => {
  initChartDefaults();
  initMap();
  addAirportMarkers().catch((error) => console.error("Could not load airports", error));
  initTabs();
  initAssistant();
  refreshHealth();
  setInterval(refreshHealth, 30_000);
});

// Handy for debugging in the browser console: window.cph.api("/api/airports")
window.cph = { api, addLayer, clearLayer, renderPlaceholder, getMap, cssVar, chartPalette, escapeHtml };
