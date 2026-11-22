// Disruptions track. Guide: docs/track-3-disruptions.md
import { renderPlaceholder } from "../app.js";

/** Called every time the "Disruptions" tab is shown. `panel` is the tab panel element. */
export function render(panel) {
  // HACK(disruptions): draw disruption circles on the map (status colours by severity, with a
  // legend), turn routes that cross an affected area red, list the impacted flights and
  // connections, and fill the "Active disruptions" KPI tile.
  renderPlaceholder(panel, "disruptions", {
    title: "show disruptions and their impact here",
    text: "Implement GET /api/disruptions/active and GET /api/disruptions/{id}/impact in src/backend/app/routers/disruptions.py, then draw circles and an impact list in src/frontend/tracks/disruptions.js. Guide: docs/track-3-disruptions.md",
  });
}
