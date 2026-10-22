---
name: write-with-stanza
description: Draft, rewrite, edit, or repurpose content for a brand connected to Stanza, including articles, social posts, emails, and website copy. Use even when the user does not mention brand voice or wants the content to stay in chat.
---

# Write with Stanza

Use the customer's current voice, relevant writing skills, and facts from Stanza
to create the requested content. Explicit user instructions take precedence over
this skill and the brand's default style.

## Before composing

1. Resolve the brand from the conversation or selected article. If needed, use
   `list_organizations` to find accessible projects. Ask which brand only when
   the choice is ambiguous. Use that project's ID as `brand` for context tools
   and as `projectId` for article tools; keep all retrievals scoped to it.
2. Call `get_voice` before composing each new writing or rewriting request,
   including follow-up requests and work that stays in chat. Apply the returned
   choices, examples, and never-dos even when the user did not say "in our voice."
   Reuse that result while completing the request; fetch again for a new request
   or a different brand. When the user explicitly requests another style, honor
   it. If voice guidance is missing or cannot be retrieved, say so; use the
   user's supplied style or offer a neutral draft without claiming it matches
   the brand. Never invent saved guidance.
3. For a channel or format, call `list_skills` and use `read_skill` to load the
   relevant customer skill. An explicitly named skill can be loaded directly by
   slug. Read its supporting files when needed. If no skill matches, continue
   using the requested format and the voice guidance. Ask about material
   conflicts between customer guidance when the user's request doesn't resolve
   them.
4. Gather the facts needed for this piece with `get_context`, `search_context`,
   and `read_context_file`. Read an existing article with `read_article` before
   rewriting it. Follow source links when a claim needs support; do not turn
   missing or conflicting information into confident product claims.

Tool names above are the Stanza operations. Use the names exposed by the host,
which may prefix them with the server or plugin name. If Stanza tools are not
available, explain that Stanza needs to be connected; do not pretend retrieval
succeeded. If product facts cannot be retrieved, use facts the user supplied or
ask for the missing information. A neutral voice is not permission to invent
product details.

## Compose and deliver

Write the content yourself using the retrieved guidance. Check the result
against the voice's examples and never-dos, the applicable customer skill, and
the user's requested audience, length, and purpose. Check factual claims and
calls to action against the sources too: do not invent setup steps, controls,
or product capabilities. Keep source notes outside
the finished copy unless citations belong in the requested format.

Keep the result in chat when requested. When the user asks to save a new draft,
use `create_draft` and return its editor link. To change an existing article,
use `read_article` then `edit_article`, preserving unrelated text. Follow the
tools' editor-opening and retry instructions for the current host. Saving a
draft does not publish it.

This writing workflow does not apply to factual lookups, creating blank drafts,
saving supplied text verbatim, or mechanical changes such as fixing a typo or
formatting. Preserve the user's exact text in those cases; don't introduce a
voice rewrite. It also does not change the assistant's ordinary conversational
voice or apply to unrelated coding tasks.
