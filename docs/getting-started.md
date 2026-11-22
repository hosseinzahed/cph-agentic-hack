# Getting started: fork or clone

← [Docs index](README.md) · Next: [Workshop flow](workshop-flow.md)

There are two ways to get the starter. Pick **one per team** before the workshop starts. The code,
the setup and the track guides are the same for both. The only differences are **where your
issues, branches and pull requests go**.

| | **Path A · Fork** (recommended) | **Path B · Clone** |
|---|---|---|
| Best for | Teams that want their own copy on GitHub, with no write access to the event repo needed | Teams the organisers added as collaborators on the event repo, or anyone working only locally |
| Your GitHub repo | `<you>/cph-agentic-hack` (public, like the original) | The event repo `hosseinzahed/cph-agentic-hack`, shared with the other teams |
| `origin` remote | Your fork | The event repo |
| `upstream` remote | The event repo (to pull organiser fixes) | — |
| Issues, branches, PRs | In **your fork** | In the **event repo**, with a team prefix |
| Branch name | `track/<track>` | `<team>/<track>`, e.g. `team-falcon/flights` |
| `@architect`, coding agent, PR, Copilot code review | ✅ | ✅ with write access · ❌ local only (see [B2](#b2-clone-without-write-access-local-only)) |

`<track>` is one of `onboarding`, `flights`, `disruptions` or `gates`. After either path, continue
with **[Set up and run](#both-paths-set-up-and-run)**.

---

## Path A · Fork

### A1. Fork and clone

With the GitHub CLI (one command forks, clones and sets up both remotes):

```bash
gh repo fork hosseinzahed/cph-agentic-hack --clone
cd cph-agentic-hack
```

Or in the browser: open https://github.com/hosseinzahed/cph-agentic-hack, select **Fork** →
**Create fork**, then clone **your fork** and add the original as `upstream`:

```bash
git clone https://github.com/<you>/cph-agentic-hack.git
cd cph-agentic-hack
git remote add upstream https://github.com/hosseinzahed/cph-agentic-hack.git
```

> Fork into your personal account, or into a team organisation that allows forking. A fork of a
> public repository is public, so never commit secrets or real data. (You should never do that anyway.)

### A2. Turn on Issues in your fork

GitHub **disables Issues on new forks**, and `@architect` needs them to create your tasks.

```bash
gh repo edit <you>/cph-agentic-hack --enable-issues
```

Or go to **Settings → General → Features** in your fork and tick **Issues**.

### A3. Point the GitHub CLI at your fork

`gh repo fork --clone` makes the **original** repo the default for `gh` commands, so
`gh pr create` and `gh issue create` would target the event repo. Switch the default to your fork:

```bash
gh repo set-default <you>/cph-agentic-hack
gh repo set-default --view      # should print <you>/cph-agentic-hack
```

### A4. Check

```bash
git remote -v
# origin    https://github.com/<you>/cph-agentic-hack.git
# upstream  https://github.com/hosseinzahed/cph-agentic-hack.git
```

✅ `origin` is your fork, `upstream` is the event repo, and your fork has an **Issues** tab.

### A5. Get organiser fixes during the day (if announced)

```bash
git checkout main
git pull upstream main
git push origin main
git checkout track/<track> && git merge main
```

Or select **Sync fork** on your fork's GitHub page, then `git pull` locally.

---

## Path B · Clone

### B1. Clone with write access (shared event repo)

Use this path when the organisers have added your team as collaborators.

```bash
git clone https://github.com/hosseinzahed/cph-agentic-hack.git
cd cph-agentic-hack
```

Several teams share this repo, so:

- **Prefix every branch with your team name**: `<team>/<track>`, e.g. `team-falcon/flights`.
  Never push to `main`.
- Tell `@architect` your team name. It adds a `team:<team>` label (if the label exists) and
  puts `[<team>]` in the issue titles.
- Open pull requests against `main`, but **don't merge** them unless the organisers ask you to.

✅ `git remote -v` shows only `origin` → `hosseinzahed/cph-agentic-hack`, and
`git push origin <team>/<track>` works.

### B2. Clone without write access (local only)

Without write access you can do every **local** step: setup, instructions, agent mode, skills,
prompt files, the Copilot SDK assistant, tests and `@reviewer`. Steps that write to GitHub won't
work: issues from `@architect`, pushing a branch, the coding agent, pull requests and Copilot
code review.

To unlock them, publish your clone as **your own repository**. Unlike a fork, it can be private:

```bash
git remote rename origin upstream
gh repo create cph-agentic-hack-<team> --private --source . --remote origin --push
gh repo set-default <you>/cph-agentic-hack-<team>
```

From then on, follow the **Fork** conventions (branch `track/<track>`, PRs inside your own repo).

---

## Both paths: set up and run

From the repository root:

| Windows (PowerShell) | macOS / Linux |
|---|---|
| `.\src\scripts\setup.ps1` | `./src/scripts/setup.sh` |
| `python src\scripts\check_env.py` | `python src/scripts/check_env.py` |

Then run `uvicorn backend.app.main:app --app-dir src --reload` and open http://localhost:8000.

🖥️ **GitHub Copilot app:** connect the folder with **+ → Open local folder** (after you fork and clone)
or **+ → Add GitHub repository** (your fork, or the event repo). Run the setup in that folder, and
start sessions with **Workspace: Current checkout**. See [copilot-app.md](copilot-app.md).
If anything fails, see [Troubleshooting in the README](../README.md#troubleshooting).

## Where things go in each workshop step

| Workshop step | Fork (or published clone) | Clone with write access |
|---|---|---|
| `@architect` creates issues | Your repo (check the URL it reports) | Event repo, `[<team>]` in titles, `team:<team>` label |
| `@architect` creates the branch | `track/<track>` | `<team>/<track>` |
| Assign an issue to the Copilot coding agent | Your repo | Event repo (your team's issue only) |
| Open the pull request | Base: **`<you>/cph-agentic-hack` → `main`** | Base: `hosseinzahed/cph-agentic-hack` → `main` |
| 🖥️ GitHub Copilot app: **Create PR** | Check that the base repository is your fork | Check the title has your `[<team>]` prefix |
| Request a Copilot code review | On that pull request | On that pull request |

> ⚠️ **Fork users:** on GitHub's **Compare & pull request** page, the default *base repository*
> is the **original** repo. Change it to **your fork** before you select **Create pull request**.
> With the CLI: `gh pr create --repo <you>/cph-agentic-hack --base main`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `@architect` or `gh issue create` targets the wrong repo | Run `gh repo set-default <you>/cph-agentic-hack` and tell `@architect` the repo explicitly: "Create the issues in `<you>/cph-agentic-hack`." |
| No **Issues** tab on your fork | Enable it (step [A2](#a2-turn-on-issues-in-your-fork)). |
| PR opened against `hosseinzahed/cph-agentic-hack` by mistake | Close it and open a new one with your fork as the base repository. |
| `Permission denied` / `403` on `git push` | You cloned without write access: use [B2](#b2-clone-without-write-access-local-only) or fork ([Path A](#path-a--fork)). |
| Branch name already exists on the shared repo | Another team chose it: prefix it with your team name (`<team>/<track>`). |
| `upstream` remote missing on your fork | `git remote add upstream https://github.com/hosseinzahed/cph-agentic-hack.git` |
