# Dexi plugin for Claude Code and Claude Cowork

Connects Claude to your [Dexi](https://dexi.net) notes via the Dexi MCP server (`https://mcp.dexi.net/mcp`). On first use, Dexi's OAuth consent page opens in your browser — sign in, choose what the connection can access (everything, or a single folder/tag), and you're connected.

## Install

**Claude Code:**

```
/plugin marketplace add dexi/claude-plugin
/plugin install dexi@dexi
```

**Claude Cowork**: Cowork tab → Customize → Plugins → Add from a repository → `https://github.com/dexi/claude-plugin`, then install "Dexi".

Or try it in Claude Code without installing by cloning this repo and running:

```
claude --plugin-dir .
```

## What you get

- **The Dexi MCP server** — all twelve tools (search, semantic search, note CRUD, tags, folders, reviews), documented at [docs.dexi.net](https://docs.dexi.net/mcp/tools). Claude uses them automatically once connected.
- **`/dexi:capture`** — save a finding, decision, or snippet from the current session as a Dexi note. Claude also invokes this itself when you say "save that to my notes".
- **`/dexi:recall`** — search your notes (keyword + semantic) and answer from what you've saved. Also model-invoked: "did I save anything about X?"
- **`/dexi:review`** — a spaced-repetition review session: question-first quizzing on your due cards, grades recorded back to Dexi. Only runs when you ask for it.

## Access control

Manage or revoke the connection in Dexi under **Settings → Connected apps**, where you can also restrict it to one folder or tag after the fact.

## About

Dexi is a note-taking and collaboration app: notes with tags, wiki-links, and semantic search, plus bookmarks, RSS subscriptions, email-to-note capture, and spaced repetition. This repo is the public distribution mirror for the Claude plugin; the plugin is developed in the main (private) Dexi repository.
