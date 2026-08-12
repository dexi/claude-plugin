---
description: Search the user's Dexi notes for saved knowledge. Use when the user asks what their notes say about something, wants to recall past research, decisions, bookmarks, or saved articles, or says "check my Dexi" / "did I save anything about…".
---

# Recall from Dexi

Find what the user has saved in Dexi about a topic using the Dexi MCP tools. If the user provided input after the skill name, that is the topic: "$ARGUMENTS".

Search strategy:

1. Run `search_notes` (keyword/full-text) and `semantic_search` (conceptual similarity) — they surface different results, so for anything non-trivial run both. Dexi notes back everything: typed notes, bookmarks, emailed-in messages, and RSS feed entries all come back from the same search.
2. Search results return snippets. Call `get_note` for the full body of the notes that actually matter before answering — don't conclude from snippets alone.
3. When one note is clearly central, `find_similar` on its id is a cheap way to pull in related notes the queries missed.
4. If the topic maps to how the user organizes things, `list_tags` / `list_folders` plus `list_notes` with a `tag` or `folder` filter beats free-text search (e.g. "what's in my #reading list").

Answer the user's question directly from what you found, citing note titles with links (`https://app.dexi.net/dashboard/notes/<id>`). If nothing relevant exists, say so plainly — don't pad with marginal matches.
