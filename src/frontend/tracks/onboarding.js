// Passenger onboarding track. Guide: docs/track-1-passenger-onboarding.md
import { renderPlaceholder } from "../app.js";

/** Called every time the "Passenger onboarding" tab is shown. `panel` is the tab panel element. */
export function render(panel) {
  // HACK(onboarding): build the queue heatmap and wait-time forecast here
  // (Chart.js line chart + a terminal × checkpoint × time heatmap), and fill the
  // "Security wait T2/T3" KPI tiles in index.html.
  renderPlaceholder(panel, "onboarding", {
    title: "build the queue heatmap and wait-time forecast here",
    text: "Implement GET /api/onboarding/queues and GET /api/onboarding/forecast in src/backend/app/routers/onboarding.py, then draw them in src/frontend/tracks/onboarding.js. Guide: docs/track-1-passenger-onboarding.md",
  });
}
