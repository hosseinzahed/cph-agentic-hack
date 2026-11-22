// Flight plans track. Guide: docs/track-2-flight-plans.md
import { renderPlaceholder } from "../app.js";

/** Called every time the "Flight plans" tab is shown. `panel` is the tab panel element. */
export function render(panel) {
  // HACK(flights): build the world route map here (great-circle lines from CPH, coloured by
  // status, via addLayer("flights:routes", ...)), a departures/arrivals board using the
  // .board and .chip styles, and fill the "Departures next hour" KPI tile.
  renderPlaceholder(panel, "flights", {
    title: "build the world route map here",
    text: "Implement GET /api/flights/routes (GeoJSON) and GET /api/flights in src/backend/app/routers/flights.py, then draw routes on the map and a departures/arrivals board in src/frontend/tracks/flights.js. Guide: docs/track-2-flight-plans.md",
  });
}
