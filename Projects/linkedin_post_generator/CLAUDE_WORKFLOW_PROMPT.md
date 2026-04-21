# How to update this workflow with Claude.ai

When you want to change the workflow, paste this entire prompt into Claude.ai
(claude.ai/new), attach or paste the current `n8n_workflow.json`, and describe
your change at the bottom.

---

## Prompt to paste into Claude.ai

```
You are helping me maintain an n8n workflow JSON file.

## What this workflow does
Fetches AI news from NewsAPI, TLDR AI (via Jina.ai), and AI Report NL (via Jina.ai),
then calls the Anthropic Claude API to generate LinkedIn posts, and emails the result
via Gmail.

## Workflow structure (sequential)
1. Schedule Trigger — Tue/Thu/Sat 8AM Berlin
2. Fetch NewsAPI — GET newsapi.org/v2/everything
3. Fetch TLDR AI — GET r.jina.ai/https://tldr.tech/ai
4. Fetch AI Report Archive — GET r.jina.ai/https://www.aireport.nl/archive
5. Extract AI Report URL — Code node, regex extracts first /p/ URL
6. Fetch AI Report Article — GET r.jina.ai/{latest article url}
7. Combine Sources — Code node, assembles text from all 3 sources
8. Build Claude Payload — Code node, builds JSON.stringify payload for Claude API
9. Claude: Generate Post — HTTP POST to api.anthropic.com/v1/messages, body is raw string from node 8
10. Extract Post Text — Code node, pulls text blocks from Claude response, builds email body
11. Send Email — Gmail node

## Rules for editing
- Never change node IDs or names — connections depend on them
- The Claude API call uses specifyBody: "string" with body: "={{ $json.payload }}" — do not change this to specifyBody: "json", it will break
- API keys appear as PASTE_X_HERE placeholders — leave them as-is
- The Build Claude Payload node uses string concatenation (not template literals) to build the user prompt — keep it that way to avoid JSON escaping issues
- max_tokens for Claude is currently 3000 — adjust only if you change the output format significantly
- All nodes use continueOnFail: true on fetch nodes so one failed source doesn't break the run

## My change request
[DESCRIBE YOUR CHANGE HERE — e.g. "Add a fourth source: fetch https://www.deeplearning.ai/the-batch/ via Jina.ai and include it in the Combine Sources node"]

Please return the complete updated workflow JSON, ready to import into n8n.
Only change what is necessary for my request. Do not restructure or reformat the rest.
```

---

## Tips

- **Paste the current `n8n_workflow.json` content** after the prompt so Claude has the actual node code
- **Be specific about your change** — "add source X", "change schedule to Monday only", "add a Slack notification node after Send Email"
- After Claude returns the updated JSON, save it as `n8n_workflow.json`, delete the old workflow in n8n, and re-import
- Re-paste your API keys into the nodes that say `PASTE_X_HERE` after each re-import
