# Consumer smoke tests

Latest recorded run: [October 22, 2026](reports/2026-10-22/README.md).

These tests run real Claude Code, Cursor Agent, or Codex sessions against a local
synthetic Stanza service. They export the current server instructions, input
schemas, annotations, and tool descriptions from a Stanza checkout. The model
chooses the tools and writes the response; no prompt tells it to fetch voice or
invoke the bundled skill.

The service fixture replaces authentication, stored brand material, and article
persistence. It strips output schemas and UI metadata because its responses and
editor are synthetic. This tests consumer discovery, sequencing, and writing;
it does not test production OAuth, billing, database behavior, editor rendering,
or marketplace installation. Codex loads the same skill through `.agents/skills`
instead of installing a plugin into the user's global configuration.

## Run

Install the Stanza checkout's dependencies with `pnpm install --frozen-lockfile`.
Use a checkout that includes `get_voice` and the new guidance. The host CLI must
be installed and signed in. From this plugin repository:

```sh
python3 tests/run-host-smoke.py claude /path/to/Stanza writing
python3 tests/run-host-smoke.py cursor /path/to/Stanza writing
python3 tests/run-host-smoke.py codex /path/to/Stanza writing
```

Pass `--mcp-only` to omit the bundled skill and exercise server guidance alone.
Claude and Cursor load a temporary copy of the plugin with its MCP endpoint
replaced by the local fixture. Claude allows only the fixture's tools plus
Read/Skill. Cursor runs noninteractively with `--force` in a fresh temporary
workspace; use this harness only with the included synthetic fixture. It does
not change installed plugins or connect to the production Stanza service.

Every run prints an artifact directory containing the exported metadata, prompt,
host transcript, tool trace, and `result.md`. Sequence checks fail the command
when required retrieval is absent, a chat-only task writes an article, or an
exact-text save changes the supplied text. Read the prose separately for voice,
factual grounding, and the user's explicit preferences. A successful exit alone
does not establish writing quality.

| Case | Expected behavior |
| --- | --- |
| `writing` | Fetch voice and the matching LinkedIn skill before writing; keep the result in chat. |
| `rewrite` | Read the article and voice before saving targeted edits. |
| `blank` | Create the requested empty draft without fetching voice. |
| `verbatim` | Save the supplied title and body exactly, without fetching voice. |
| `missing-voice` | Fetch voice, disclose that it is missing, and avoid claiming a brand match. |
| `style` | Fetch voice but honor the explicitly requested formal tone and word “schedule.” |
| `lookup` | Answer the product question without fetching voice or writing an article. |

Before publishing, also test an ambiguous brand, a switch between two brands,
and a follow-up writing request in a continuing conversation. Each retrieval and
write must stay on the selected project; a new writing request fetches current
voice again.

After the required Stanza server is deployed, install the package in a fresh
ChatGPT conversation and repeat the writing, blank, verbatim, and missing-voice
cases. Repeat through Claude chat/Cowork as well as the CLI. Local CLI results
do not establish hosted chat or directory-install behavior. Refresh/rescan tool
metadata and upload the new skill package when publishing a plugin update.
