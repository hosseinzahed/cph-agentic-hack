# CPH Agentic Hack: workshop guide

In this 2-hour hack you build an intelligent **Copenhagen Airport (CPH) operations app** with
GitHub Copilot. The starter app already runs: a FastAPI backend with a seeded SQLite database
and a CPH-themed web UI with an OpenStreetMap world map. Your team picks **one track**, plans it
with a custom agent, builds its API and visualisation with Copilot agent mode, exposes it as a
Copilot SDK tool for the **CPH Ops Assistant**, and opens a reviewed pull request. All data is
synthetic.

## Reading order

1. [getting-started.md](getting-started.md): **fork or clone** the repo, then set it up. Your choice decides where your issues, branches and PRs go.
   Using the **GitHub Copilot app** instead of VS Code? Also read [copilot-app.md](copilot-app.md).
2. [workshop-flow.md](workshop-flow.md): the 120-minute agenda and which Copilot feature you use in each step.
3. **Your track file** (table below): the detailed step-by-step guide for your team.
4. [assistant-and-finale.md](assistant-and-finale.md): the Copilot SDK step every track shares, and the cross-track finale.

## Tracks

| # | Track | Goal | Guide |
|---|---|---|---|
| 1 | Passenger onboarding (`onboarding`) | Show queue levels at check-in, security and passport control, and forecast wait times per terminal. | [track-1-passenger-onboarding.md](track-1-passenger-onboarding.md) |
| 2 | Flight plans (`flights`) | Draw the CPH route network on a world map and build the departures and arrivals board. | [track-2-flight-plans.md](track-2-flight-plans.md) |
| 3 | Potential disruptions (`disruptions`) | Show weather, ATC and strike disruptions on the map and which flights and connections they hit. | [track-3-disruptions.md](track-3-disruptions.md) |
| 4 | Gates & baggage (`gates`) | Visualise stand allocations, detect conflicts and find transfer bags at risk. | [track-4-gates-and-baggage.md](track-4-gates-and-baggage.md) |

Every track ends with the same shared step: [assistant-and-finale.md](assistant-and-finale.md).

## More

- [hack-ideas.md](hack-ideas.md): five product ideas to aim for (pick one or remix).
- [uipath-handoff.md](uipath-handoff.md): optional hand-off to UiPath robots through `automation_queue`.
- [diagrams/](diagrams/README.md): draw.io diagrams that `@architect` creates for your track.
- [copilot-app.md](copilot-app.md): doing the hack in the GitHub Copilot app instead of VS Code.
- Repository setup, Copilot features and troubleshooting: [../README.md](../README.md).

## Conventions used in the guides

- 💬 **Prompt**: paste into Copilot Chat (agent mode unless the step says otherwise).
- 🍴 **Fork** / 📥 **Clone**: a step that differs per path from [getting-started.md](getting-started.md).
- 🖥️ **App**: how to do a step in the GitHub Copilot app instead of VS Code ([copilot-app.md](copilot-app.md)).
  Prompts that start with `/new-endpoint`, `/write-tests` or `/explain-this-repo` are VS Code
  prompt files. In the app, say "Follow `.github/prompts/<name>.prompt.md` for …" instead.
- 💡 **Hint**: a concept or approach, not the solution.
- ✅ **Checkpoint**: you're on track if this is true.
- `HACK(<track>)`: a marker in the code where your track has work to do. Search for it with
  <kbd>Ctrl</kbd>/<kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>F</kbd>.
