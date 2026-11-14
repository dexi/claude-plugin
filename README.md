# Dexi plugin for Claude Code and Claude Cowork

Connects Claude to your [Dexi](https://dexi.net) notes via the Dexi MCP server (`https://mcp.dexi.net/mcp`). On first use, Dexi's OAuth consent page opens in your browser — sign in, choose what the connection can access (everything, or a single folder/tag), and you're connected. The notes are the same ones ChatGPT, Gemini and any other MCP client you connect read and write, so Claude shares one memory with them.

## Install

**Claude Code**, via the public distribution mirror ([dexi/claude-plugin](https://github.com/dexi/claude-plugin)):

```
/plugin marketplace add dexi/claude-plugin
/plugin install dexi@dexi
```

**Claude Cowork**: Cowork tab → Customize → Plugins → Add from a repository → `https://github.com/dexi/claude-plugin`, then install "Dexi".

With access to this (private) repo, `/plugin marketplace add dexi/dexi` works too in Claude Code. Or try it without installing:

```
claude --plugin-dir ./claude-plugin
```

## What you get

- **The Dexi MCP server** — all eighteen tools (search, semantic search, note CRUD, tags, folders, bases, reviews), documented at [docs.dexi.net](https://docs.dexi.net/mcp/tools). Claude uses them automatically once connected.
- **`/dexi:capture`** — save a finding, decision, or snippet from the current session as a Dexi note. Claude also invokes this itself when you say "save that to my notes".
- **`/dexi:recall`** — search your notes (keyword + semantic) and answer from what you've saved. Also model-invoked: "did I save anything about X?"
- **`/dexi:memory`** — Dexi as shared memory across assistants for the current project (the git repository's name): Claude checks Dexi for prior decisions before substantive work and saves settled ones, tagged `#memory` plus a project tag. `#memory` is also the tag the Hermes and OpenClaw plugins put on their session digests, so one tag covers every agent's memory ([Switching agents](https://docs.dexi.net/mcp/shared-memory#switching-agents)). Model-invoked, or run it at the start of a session.
- **`/dexi:review`** — a spaced-repetition review session: question-first quizzing on your due cards, grades recorded back to Dexi. Only runs when you ask for it.

## Data and privacy

The plugin contains no code that runs on your computer: no hooks, scripts or binaries. Everything goes through the Dexi MCP server over OAuth, and only what Claude sends in a tool call (searches, notes you save, review grades) reaches Dexi.

## Access control

Manage or revoke the connection in Dexi under **Settings → Connected apps**, where you can also restrict it to one folder or tag after the fact.

## License

MIT — see [LICENSE](LICENSE).
