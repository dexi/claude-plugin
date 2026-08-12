---
description: Save something to the user's Dexi notes. Use when the user wants to save, capture, note down, or remember something — a finding, decision, code snippet, summary, or link — or says "add this to Dexi" / "save that to my notes".
---

# Capture to Dexi

Save the current finding, decision, or content the user pointed at as a Dexi note using the Dexi MCP `create_note` tool. If the user provided input after the skill name, that is what to capture: "$ARGUMENTS".

How to write the note:

1. **Distill, don't dump.** A note should be the useful conclusion, not a transcript. For a debugging finding: the symptom, root cause, and fix. For a decision: what was decided and why. For research or a meeting: the takeaways, not the play-by-play. Short excerpts or code snippets are fine when they're the point; never paste pages of material.
2. **Title**: a short, specific noun phrase the user could find again later (e.g. "Railway healthchecks probe PORT, not the domain target port").
3. **Tags**: write 1–3 relevant `#hashtags` inline in the body — Dexi parses them into tags automatically. Reuse the user's existing vocabulary when known (call `list_tags` if unsure rather than inventing near-duplicates).
4. **Body**: plain text. `[[Wiki Links]]` to related note titles are supported and encouraged when you know a related note exists.

Call `create_note` with the title and body. Then confirm to the user with the note title and its link: `https://app.dexi.net/dashboard/notes/<id>` (using the `id` from the tool result).

If `create_note` fails because the note limit was reached, relay the message and mention upgrading at https://dexi.net/pricing — don't retry.
