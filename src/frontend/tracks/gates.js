// Gates & baggage track. Guide: docs/track-4-gates-and-baggage.md
import { renderPlaceholder } from "../app.js";

/** Called every time the "Gates & baggage" tab is shown. `panel` is the tab panel element. */
export function render(panel) {
  // HACK(gates): build the stand allocation Gantt chart (Chart.js horizontal floating bars),
  // the conflict list and the count of transfer bags at risk here.
  renderPlaceholder(panel, "gates", {
    title: "build the stand Gantt chart, conflicts and bags at risk here",
    text: "Implement GET /api/gates/allocations, GET /api/gates/conflicts and GET /api/baggage/at-risk in src/backend/app/routers/gates.py, then draw them in src/frontend/tracks/gates.js. Guide: docs/track-4-gates-and-baggage.md",
  });
}
