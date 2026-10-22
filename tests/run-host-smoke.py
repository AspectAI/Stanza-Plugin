"""Run a real consumer against synthetic Stanza data and exported production metadata.

Usage: python3 tests/run-host-smoke.py claude|cursor|codex STANZA_CHECKOUT CASE [--mcp-only]
Artifacts go to a new temporary workspace; no installed plugins are changed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

host, checkout, case, *options = sys.argv[1:]
if host not in ('claude', 'cursor', 'codex'):
    raise SystemExit('Host must be claude, cursor, or codex')
prompts = {
    'writing': 'Write a short LinkedIn post for Fambot announcing shift swaps. Keep it in chat.',
    'rewrite': 'Rewrite the introduction of the Fambot article Shift swaps to make it clearer. Save the changes. Keep the editor closed.',
    'verbatim': 'Save a new Fambot draft titled Office hours with exactly this body: We are open from nine to five. Do not rewrite it. Keep the editor closed.',
    'blank': 'Create a blank Fambot draft titled Notes. Do not write anything yet. Keep the editor closed.',
    'missing-voice': 'Write a short LinkedIn post for Fambot announcing shift swaps. Keep it in chat.',
    'style': 'Write a short Fambot shift-swap announcement in a deliberately formal tone, using schedule rather than rota for this piece. Keep it in chat.',
    'lookup': 'What does Fambot say about payroll integrations? Just answer the factual question.',
}
prompt = prompts[case] + ' Use only the connected Stanza service for brand information; do not access other services or the web.'
root = Path(__file__).resolve().parent.parent
app = Path(checkout).resolve() / 'apps/app'
run = Path(tempfile.mkdtemp(prefix=f'stanza-{host}-{case}-'))
metadata = run / 'metadata.json'
export = """
import {writeFileSync} from 'node:fs';
import {Client, InMemoryTransport} from '@modelcontextprotocol/client';
import serverModule from './src/lib/mcp/server.ts';
const server = serverModule.createStanzaMcpServer({userId:'fixture',scopes:['read','write']}, {
  access:{withBrands:async()=>{throw new Error('Metadata export only')}},
  rateLimit:async()=>{}, baseURL:()=> 'https://stanza.test'
});
const [ct, st] = InMemoryTransport.createLinkedPair();
const client = new Client({name:'metadata-export',version:'1'});
await server.connect(st); await client.connect(ct);
writeFileSync(process.argv[2], JSON.stringify({instructions:client.getInstructions(),tools:(await client.listTools()).tools}));
await client.close(); await server.close();
"""
subprocess.run([shutil.which('node'), '--import', 'tsx', '--input-type=module', '-', str(metadata)],
               input=export, text=True, cwd=app, env={**os.environ, 'SKIP_ENV_VALIDATION': '1'}, check=True)
if not metadata.exists():
    raise SystemExit('Metadata export did not create its output')
fixture = {'command': shutil.which('node'), 'args': [str(root / 'tests/support/mcp-fixture.mjs'), str(metadata), str(run / 'trace.jsonl')]}
if case == 'missing-voice':
    fixture['env'] = {'STANZA_FIXTURE_MISSING_VOICE': '1'}
(run / 'mcp.json').write_text(json.dumps({'mcpServers': {'stanza': fixture}}))
(run / 'prompt.txt').write_text(prompt)
plugin_args = []
if '--mcp-only' not in options:
    plugin = run / 'plugin'
    shutil.copytree(root, plugin, ignore=shutil.ignore_patterns('.git', 'tests'))
    portable = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json', 'mcpServers': {'stanza': {'type': 'stdio', **fixture}}}
    (plugin / 'mcp.json').write_text(json.dumps(portable))
    manifest = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
    manifest['mcpServers'] = {'stanza': {'type': 'stdio', **fixture}}
    (plugin / '.claude-plugin/plugin.json').write_text(json.dumps(manifest))
    plugin_args = ['--plugin-dir', str(plugin)]
if host == 'claude':
    command = ['claude', '-p', '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
               '--setting-sources', '', '--strict-mcp-config', '--mcp-config', str(run / 'mcp.json'),
               '--tools', 'Read,Skill', '--allowedTools', 'mcp__stanza', 'Skill', 'Read', '--permission-mode', 'dontAsk', *plugin_args]
elif host == 'cursor':
    (run / '.cursor').mkdir()
    (run / '.cursor/mcp.json').write_text((run / 'mcp.json').read_text())
    command = ['agent', '--print', '--output-format', 'stream-json', '--workspace', str(run),
               '--trust', '--approve-mcps', '--force', *plugin_args, prompt]
else:
    if plugin_args:
        shutil.copytree(root / 'skills', run / '.agents/skills')
    command = ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
               '--json', '--sandbox', 'read-only', '-c', 'approval_policy="never"',
               '-c', f'mcp_servers.stanza.command={json.dumps(fixture["command"])}',
               '-c', f'mcp_servers.stanza.args={json.dumps(fixture["args"])}']
    for key, value in fixture.get('env', {}).items():
        command += ['-c', f'mcp_servers.stanza.env.{key}={json.dumps(value)}']
    command += [prompt]
print(f'Artifacts: {run}', flush=True)
with (run / 'transcript.jsonl').open('w') as output, (run / 'stderr.log').open('w') as errors:
    completed = subprocess.run(command, input=prompt if host == 'claude' else None, text=True,
                               cwd=run, stdout=output, stderr=errors, timeout=240)
events = [json.loads(line) for line in (run / 'transcript.jsonl').read_text().splitlines() if line.startswith('{')]
trace = run / 'trace.jsonl'
calls = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
answer = '\n'.join(str(event.get('result', '')) for event in events if event.get('type') == 'result')
if host == 'codex':
    answer = '\n'.join(event['item']['text'] for event in events
                       if event.get('type') == 'item.completed' and event.get('item', {}).get('type') == 'agent_message')
sequence = [call['tool'] for call in calls]
failures = []
if not calls:
    failures.append('No fixture tool calls completed')
if case in ('writing', 'rewrite', 'missing-voice', 'style') and 'get_voice' not in sequence:
    failures.append('Voice was not retrieved')
if case == 'writing' and 'read_skill' not in sequence:
    failures.append('Matching channel skill was not loaded')
if case in ('writing', 'missing-voice', 'style', 'lookup') and any(tool in sequence for tool in ('create_draft', 'edit_article')):
    failures.append('Chat-only task mutated an article')
if case in ('blank', 'verbatim', 'lookup') and 'get_voice' in sequence:
    failures.append('Voice retrieved for an exempt task')
if case in ('blank', 'verbatim'):
    expected = {'title': 'Notes', 'markdown': ''} if case == 'blank' else {'title': 'Office hours', 'markdown': 'We are open from nine to five.'}
    if 'create_draft' not in sequence or calls[-1]['article'] != expected:
        failures.append('Saved article did not match the requested exact text')
if case == 'rewrite' and ('edit_article' not in sequence or 'read_article' not in sequence or
                          ('get_voice' in sequence and sequence.index('get_voice') > sequence.index('edit_article'))):
    failures.append('Rewrite did not read voice and article before editing')
skill_calls = [part.get('input') for event in events for part in event.get('message', {}).get('content', [])
               if isinstance(part, dict) and part.get('name') == 'Skill']
loading = 'standalone .agents/skills discovery' if host == 'codex' else 'native --plugin-dir'
report = f'# {host}: {case}\n\nBundled skill supplied: {bool(plugin_args)} ({loading})\n\nPrompt: {prompt}\n\nCalls: {" → ".join(sequence)}\n\nSkill invocations: {skill_calls}\n\nSequence checks: {failures or "passed; review the prose separately"}\n\n## Answer\n\n{answer}\n'
if calls:
    report += f'\n## Final fixture article\n\n```json\n{json.dumps(calls[-1]["article"], indent=2)}\n```\n'
(run / 'result.md').write_text(report)
print(report, flush=True)
raise SystemExit(completed.returncode or bool(failures))
