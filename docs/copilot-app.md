# Using the GitHub Copilot app

← [Docs index](README.md) · [Getting started](getting-started.md) · [Workshop flow](workshop-flow.md)

You can do the whole hack in the **[GitHub Copilot app](https://github.com/features/ai/github-app)**
instead of VS Code. The app is a desktop app built on Copilot CLI: you work in **agent sessions**,
review **Changes**, open PRs, and preview the running app in a **Browser canvas**. Most of the
repo's Copilot setup works unchanged. This page lists what's different.

Teams can mix: some people in VS Code, some in the app, all on the same branch.

## 1. Install and connect the repo

1. Install the app from https://github.com/features/ai/github-app and **sign in to GitHub**.
   Copilot Business/Enterprise: the "GitHub Copilot app" policy must be enabled (it's on by default).
2. Install **Python 3.11+** and **Git** (the app doesn't install them).
3. Connect the repository. In the sidebar, select **+** next to **Sessions**:

   | Your path ([getting-started.md](getting-started.md)) | In the app |
   |---|---|
   | 🍴 Fork | Fork first (`gh repo fork hosseinzahed/cph-agentic-hack --clone`, or **Fork** on GitHub.com). Then use **Open local folder** on the clone, or **Add GitHub repository** and pick `<you>/cph-agentic-hack`. Still do steps [A2](getting-started.md#a2-turn-on-issues-in-your-fork) (enable Issues) and [A3](getting-started.md#a3-point-the-github-cli-at-your-fork) (`gh repo set-default`). |
   | 📥 Clone | **Add GitHub repository** → `hosseinzahed/cph-agentic-hack`, or **Open local folder** on a clone you already have. |

4. Run the setup **once** in the folder you connected. Ask in a session, or run it in a terminal:
   `.\src\scripts\setup.ps1` (Windows) or `./src/scripts/setup.sh` (macOS/Linux).

## 2. Start a session: pick the workspace

When you start a session, choose the **Workspace** dropdown below the prompt box:

| Workspace | Use it when | Remember |
|---|---|---|
| **Current checkout** (recommended for the hack) | One session per person, working on your track branch | `.venv` and `src/backend/data/cph.db` from setup are already there |
| **New worktree** | You want parallel sessions (e.g. API and UI at the same time) | A worktree is a fresh checkout **without git-ignored files**: run the setup script in it first (or ask the agent to), and start uvicorn on another port (`--port 8001`) if 8000 is taken |

Keep **Environment** on **This computer**: the app needs your local Python, the SQLite file and
`localhost`. **Cloud** sessions run in a GitHub-hosted sandbox. They're useful as an alternative to
the coding agent (see the table below), but you can't preview them on your `localhost`.

Session modes map to the workshop: **Plan** for planning, **Interactive** while you learn,
**Autopilot** for well-scoped tasks. For tool permissions, **Assisted** is a good default.

## 3. Run and preview the app

💬 "Start the app with `uvicorn backend.app.main:app --app-dir src --reload` in the background and open http://localhost:8000 in a browser canvas."

The Browser canvas sits next to the chat, so you can ask Copilot to check the page for you
("Take a screenshot of the Flight plans tab and check the console for errors"). A Terminal canvas
works too, if you want to watch the server log.

## 4. Copilot features: VS Code vs. the app

| Feature in this repo | VS Code | GitHub Copilot app |
|---|---|---|
| Repo instructions (`.github/copilot-instructions.md`) and path instructions (`.github/instructions/*.instructions.md`) | Automatic | Automatic, same files and `applyTo` patterns |
| Custom agents (`@architect`, `@map-builder`, `@reviewer`) | Agent picker | Agent picker in the prompt box, or `/agent` |
| `@architect` **handoff** button | ✅ | Not shown. When the plan is done, switch back to the default agent (or start a new session) and say "Implement issue #N". |
| Skills (`.github/skills/*`) | Automatic / `/` menu | Automatic; listed under **Customize → Skills**, and in the `/` picker |
| Prompt files (`.github/prompts/*.prompt.md`) | `/new-endpoint`, `/write-tests`, `/explain-this-repo` | Not run as slash commands. Reference the file instead: "Follow `.github/prompts/new-endpoint.prompt.md` for `GET /api/flights`" (or attach it with `@`). |
| MCP servers (GitHub, Microsoft Learn, draw.io) | `.vscode/mcp.json` | `.mcp.json` at the repo root (same three servers); check them under **Customize → MCP → Installed** |
| Draw.io diagrams in `docs/diagrams/` | Draw.io Integration extension | The draw.io MCP server renders diagrams inline in the chat; open saved `.drawio` files at https://app.diagrams.net |
| Run tests | Testing view | Ask "Run pytest and fix failures", or run `pytest` in a terminal |
| Copilot coding agent | Assign an issue on GitHub.com | Same, or open the issue from **Issues** in the sidebar and start a session from it (choose **Cloud** to run it off your machine) |
| Open a pull request | `gh pr create` / GitHub.com | **Create PR** above the prompt box, then **PR** to view it in the app |
| Copilot code review | Request **Copilot** as a reviewer on the PR | Same (on the PR on GitHub.com). Extras before you push: `/security-review` and `/rubber-duck` |

## 5. Prompt cheat sheet for the app

The track guides use VS Code prompt-file shortcuts. In the app, use these instead:

| Track guide says | Type in the app |
|---|---|
| `/explain-this-repo` | "Follow `.github/prompts/explain-this-repo.prompt.md`. My track is `<track>`." |
| `/new-endpoint GET /api/...` | "Follow `.github/prompts/new-endpoint.prompt.md` for `GET /api/...`." |
| `/write-tests` with a router selected | "Follow `.github/prompts/write-tests.prompt.md` for `src/backend/app/routers/<track>.py`." |
| "@architect …" / "@map-builder …" / "@reviewer …" | Select the agent in the picker (or `/agent`), then send the rest of the prompt |
| "Use the copilot-sdk-tool skill to …" | Same prompt (skills load automatically) |

## 6. Fork users: check the PR target

**Create PR** opens the PR for your session's branch. After it opens, check that the PR's
**base repository** is **your fork**, not `hosseinzahed/cph-agentic-hack`. If it's wrong,
close it and run `gh pr create --repo <you>/cph-agentic-hack --base main`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError` / "No module named uvicorn" in a session | The session is in a **new worktree** without `.venv`: run the setup script there, or start the session with **Current checkout**. |
| Header says "API ok · run the seed script" | The worktree has no `cph.db`: `python src/backend/scripts/seed.py`. |
| `/new-endpoint` isn't in the `/` picker | Expected: prompt files are a VS Code feature. Use the cheat sheet above. |
| `@architect` can't create issues or diagrams | Check **Customize → MCP → Installed** for `github`, `microsoft-learn` and `drawio`, and your org's MCP policy. Fork users: enable Issues ([A2](getting-started.md#a2-turn-on-issues-in-your-fork)). |
| Port 8000 already in use | Another session or worktree runs the app: use `--port 8001`. |
| Agent keeps asking for approval | Change **Tool permissions** to **Assisted** for the session. Don't use **Approve all** on code you haven't reviewed. |
