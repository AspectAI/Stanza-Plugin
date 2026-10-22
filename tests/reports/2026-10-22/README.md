# Voice workflow smoke results — October 22, 2026

Tested with the MCP metadata from Stanza commit `c8174a2a`, on top of the
`get_voice`/Context changes in PR 259. All requests used synthetic Fambot data.
See [the harness instructions](../../README.md) to reproduce them.

| Consumer | Loading path | Verified cases |
| --- | --- | --- |
| Claude Code 2.1.306 | Native plugin via `--plugin-dir` | Writing, rewrite, blank, verbatim, missing voice, explicit style, factual lookup |
| Cursor Agent 2026.10.19-6bbf2c4 | Portable plugin via `--plugin-dir` | Writing, rewrite, blank, verbatim, missing voice, explicit style, factual lookup |
| Codex CLI 0.162.1 | Same skill through local `.agents/skills` discovery | Writing |
| Claude Code and Cursor Agent | MCP connection alone, no bundled skill | Writing |

All 17 final runs passed the harness's tool-sequence and exact-save checks.
These are one-run smoke checks, not an estimated reliability rate.

The ordinary writing prompt said “Write a short LinkedIn post for Fambot
announcing shift swaps. Keep it in chat.” It did not ask for voice or name a
skill. All three hosts fetched `get_voice` and the matching customer channel
skill before returning the post. Claude invoked `stanza:write-with-stanza`;
Cursor read the packaged SKILL.md; Codex read the same SKILL.md from its local
skill directory. The MCP-only controls also retrieved voice and channel guidance.

Blank and verbatim cases called `create_draft` without `get_voice` and retained
the exact title and body. Rewrites read the live article and voice before
`edit_article`. Missing-voice cases disclosed the gap and labeled their output
neutral. Explicit style requests used “schedule” despite the voice preferring
“rota.” Factual lookups skipped voice retrieval.

## Writing review and limits

The final writing samples applied the observable voice constraints: “rota,” no
hype, no hashtags or emoji, and a concrete next action. They used the three
short paragraphs requested by the customer skill. The retrieved information
was used, not merely fetched.

Grounding still needs editorial review: Claude sometimes inferred interface
steps or benefits absent from the fixture, including opening a schedule and
selecting a shift. An early run invented a “switch on shift swaps” control;
the skill was tightened to check claims and calls to action, and the writing
case was rerun. Passing the voice checks does not establish factual accuracy
or guarantee the workflow in future requests.

Initial harness runs encountered CLI permission defaults. The harness now
allows the local synthetic tools explicitly. Its missing-voice fixture was
also corrected so a second read cannot return a voice page after `get_voice`
reports it absent; those cases were rerun. These setup attempts are excluded
from the 17 final runs.

Hosted ChatGPT and Claude chat/Cowork, directory installation, ongoing
conversations, and multi-brand switching remain unverified. The production
server must first deploy the required tools. The fixtures do not exercise
OAuth, billing, live editor rendering, or production persistence.

Portable manifests pass the Agent Plugins JSON schemas; the skill passes the
skill-creator validator; Claude's runtime manifest validator passes. Claude's
separate directory profile reports a missing license. No license was chosen
or granted by this change.

## Saved artifacts

- [Claude writing](claude-writing.md)
- [Cursor writing](cursor-writing.md)
- [Codex writing](codex-writing.md)
- [Claude missing voice](claude-missing-voice.md)
- [Cursor missing voice](cursor-missing-voice.md)

The harness also produces each run's full tool trace, final synthetic article,
and host transcript in the temporary artifact directory it prints. Only final
answers and observed tool sequences are included here.
