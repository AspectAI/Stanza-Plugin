// Consumer smoke fixture: real exported tool metadata, synthetic service responses.
// Nothing connects to Stanza, writes to a database, or opens a real editor.
import {appendFileSync, readFileSync} from 'node:fs'
import {createInterface} from 'node:readline'

const [metadataPath, tracePath] = process.argv.slice(2)
if (!metadataPath || !tracePath) throw new Error('Usage: node mcp-fixture.mjs metadata.json trace.jsonl')
const metadata = JSON.parse(readFileSync(metadataPath, 'utf8'))
const missingVoice = process.env.STANZA_FIXTURE_MISSING_VOICE === '1'
const projectId = '5c1f7a2e-4d6b-4f3a-9b0e-2a8c1d3e5f70'
const documentId = '7bf6b553-0287-4c91-a03f-928e34b05d65'
const product = 'Fambot shift swaps let a team member offer a shift to a teammate. The manager approves the swap. Available now; payroll integrations are not available.'
const voice = 'Write plainly and practically for shift managers. Use "rota" instead of "schedule". No emoji, hashtags, or hype such as "unlock", "revolutionize", or "game-changing". End with one concrete next action.'
let article = {title: 'Shift swaps', markdown: 'Unlock game-changing scheduling. Fambot makes shift swaps easy. Ask your manager to approve the swap.'}

function call(name, input) {
  if (input.brand && ![projectId, 'Fambot', 'fambot'].includes(input.brand)) {
    return {isError: true, content: [{type: 'text', text: 'Unknown brand. Only Fambot is available in this fixture.'}]}
  }
  let text
  let structuredContent
  switch (name) {
    case 'list_organizations':
      text = JSON.stringify({organizations: [{name: 'Fambot', projects: [{id: projectId, name: 'Fambot'}]}]})
      break
    case 'list_stanza_projects_and_articles':
      text = JSON.stringify({projects: [{id: projectId, name: 'Fambot'}], articles: [{id: documentId, title: article.title}]})
      break
    case 'get_context':
      text = `Fambot (${projectId}). index.md: Rota software for shift managers. Files: ${missingVoice ? '' : 'brand/voice.md, '}references/product/shift-swaps.md, articles/shift-swaps.md.`
      break
    case 'get_voice':
      text = missingVoice
        ? 'Fambot has no voice page yet. Do not invent a brand voice; tell the user.'
        : `# Fambot voice (brand/voice.md)\n${voice}`
      break
    case 'list_skills':
      text = '`linkedin-post` — LinkedIn post: Use for a short LinkedIn post about Fambot.'
      break
    case 'read_skill':
      text = input.slug === 'linkedin-post'
        ? '# LinkedIn post\nWrite three short paragraphs, under 100 words total. No heading, hashtags, or emoji. Apply the brand voice and use supported facts.'
        : 'No matching skill. Available: linkedin-post.'
      break
    case 'search_context':
      text = `references/product/shift-swaps.md\n${product}`
      break
    case 'read_context_file':
      if (input.path === 'brand/voice.md') {
        if (missingVoice) throw new Error('Fambot has no voice page yet.')
        text = voice
      } else if (input.path === 'articles/shift-swaps.md') {
        text = article.markdown
      } else if (input.path === 'references/product/shift-swaps.md') {
        text = product
      } else {
        throw new Error('File not found. Use the paths returned by get_context or search_context.')
      }
      break
    case 'read_article':
      text = JSON.stringify({projectId, documentId, ...article, editToken: 'fixture-token'})
      break
    case 'create_draft':
      article = {title: input.title ?? '', markdown: input.markdown ?? ''}
      structuredContent = {projectId, documentId, ...article, path: 'articles/shift-swaps.md', editorUrl: `https://stanza.test/projects/${projectId}/editor?article=${documentId}`}
      text = JSON.stringify(structuredContent)
      break
    case 'edit_article':
      if (input.editToken !== 'fixture-token') throw new Error('Read the article before editing it.')
      for (const edit of input.edits ?? []) {
        if (article.markdown.split(edit.oldText).length !== 2) throw new Error('Exact text must match once.')
        article.markdown = article.markdown.replace(edit.oldText, edit.newText)
      }
      if (input.title !== undefined) article.title = input.title
      text = JSON.stringify({projectId, documentId, ...article})
      break
    case 'open_stanza_editor':
      text = 'Synthetic editor opened; no browser or live document is involved.'
      break
    default:
      throw new Error(`Unsupported fixture tool: ${name}`)
  }
  return {content: [{type: 'text', text}], ...(structuredContent ? {structuredContent} : {})}
}

for await (const line of createInterface({input: process.stdin})) {
  let request
  try {
    request = JSON.parse(line)
    if (request.id === undefined) continue
    let result
    switch (request.method) {
      case 'initialize':
        result = {protocolVersion: request.params.protocolVersion, capabilities: {tools: {}}, serverInfo: {name: 'stanza-fixture', version: '1.0.0'}, instructions: metadata.instructions}
        break
      case 'tools/list':
        result = {tools: metadata.tools
          .filter(tool => !tool._meta?.ui?.visibility || tool._meta.ui.visibility.includes('model'))
          .map(({outputSchema, _meta, ...tool}) => tool)}
        break
      case 'tools/call':
        try {
          result = call(request.params.name, request.params.arguments ?? {})
        } catch (error) {
          result = {isError: true, content: [{type: 'text', text: error.message}]}
        }
        appendFileSync(tracePath, `${JSON.stringify({tool: request.params.name, input: request.params.arguments, result, article})}\n`)
        break
      case 'resources/list':
        result = {resources: []}
        break
      case 'prompts/list':
        result = {prompts: []}
        break
      case 'ping':
        result = {}
        break
      default:
        throw new Error(`Unsupported fixture method: ${request.method}`)
    }
    process.stdout.write(`${JSON.stringify({jsonrpc: '2.0', id: request.id, result})}\n`)
  } catch (error) {
    process.stdout.write(`${JSON.stringify({jsonrpc: '2.0', id: request?.id ?? null, error: {code: -32603, message: error.message}})}\n`)
  }
}
