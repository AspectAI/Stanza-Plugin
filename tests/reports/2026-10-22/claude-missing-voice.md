# claude: missing-voice

Bundled skill supplied: True (native --plugin-dir)

Prompt: Write a short LinkedIn post for Fambot announcing shift swaps. Keep it in chat. Use only the connected Stanza service for brand information; do not access other services or the web.

Calls: get_voice → list_skills → search_context → read_skill → get_context → read_context_file → read_context_file

Skill invocations: [{'skill': 'stanza:write-with-stanza', 'args': 'Short LinkedIn post for Fambot announcing shift swaps, kept in chat'}]

Sequence checks: passed; review the prose separately

## Answer

Fambot has no saved voice page in Stanza, so this draft uses a plain, neutral tone rather than a confirmed brand voice. It follows the team's LinkedIn skill, which asks for three short paragraphs under 100 words with no heading, hashtags, or emoji.

Here is the post:

Shift swaps are now available in Fambot.

When a team member can't make a shift, they can offer it to a teammate directly in Fambot. The manager reviews and approves the swap, so the rota stays accurate and nothing changes without a sign-off.

Less chasing, fewer gaps, and a schedule that reflects what's actually happening on the floor. Shift swaps are live for Fambot teams today.

Two notes on sources. The product facts come from the shift-swaps reference in Fambot's Context, which confirms the offer-to-teammate flow, manager approval, and that the feature is available now. It also states that payroll integrations are not available, so the post does not mention payroll. The one existing Fambot article on shift swaps uses phrasing like "game-changing," which I avoided since no voice guidance endorses it. If you add a voice page in Stanza, I can rework the tone to match.
