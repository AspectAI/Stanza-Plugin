# Stanza

Write and edit content using your team's current brand voice, facts, and writing
skills from Stanza. The plugin bundles the Stanza MCP connection and one shared
`write-with-stanza` skill for supported ChatGPT, Codex, Claude, and Cursor hosts.

Install the plugin through your host's supported plugin flow, connect your
Stanza account, and choose the brand when you have more than one. Try:

- "Write a LinkedIn post about our latest product launch."
- "Tighten this article's introduction."
- "Turn this article into a customer email. Keep it in chat."

The skill loads `get_voice` before composing each writing request, even when you
don't explicitly ask for brand voice. It loads matching channel skills from
Stanza and retrieves the facts needed for the piece. Your explicit style choices
take precedence. Blank drafts, exact-text saves, and mechanical edits preserve
your supplied text without a voice rewrite.

The portable `plugin.json`, `mcp.json`, and `skills/` layout serves ChatGPT,
Codex, and Cursor. `.claude-plugin/plugin.json` points Claude at the same server;
Claude discovers the same root `skills/` directory. There are no duplicated
host-specific copies of the writing skill.

Connecting only `https://app.runstanza.com/api/mcp` gives an agent the server's
tools and guidance; it does not install this bundled skill. Each host controls
skill activation and instruction following. These prompts improve consistency,
but cannot guarantee every agent will follow the workflow.

Version 0.2.0 requires `get_voice`, `get_context`, `search_context`,
`read_context_file`, `list_skills`, `read_skill`, and the article tools on the
connected server. Deploy the corresponding Stanza server changes before
publishing this plugin version. Voice and customer skills are retrieved live;
they are not copied into this package.

See [host smoke tests](tests/README.md) for the verification cases and limits.
