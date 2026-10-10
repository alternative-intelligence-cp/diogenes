# dio-r2-gemini-antigravity-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` in full. Then answer the question below as a dated, sourced digest, in the format that file gives.

**Your question:** what are all the surfaces by which Google's agent harnesses, **Gemini CLI** and **Google Antigravity**, can be integrated with an external coordination hub?

Sources:
- geminicli.com;
- the github.com/google-gemini/gemini-cli docs and releases;
- antigravity.google and its documentation;
- the Google Developers and Google Cloud blogs and docs.

Cover:

1. **Gemini CLI:**
   - MCP client support: transports, configuration, trust;
   - lifecycle hooks: does it have them? Which events, what input and output, introduced in which release?
   - extensions, and its context files (`GEMINI.md`, `AGENTS.md`);
   - headless mode (`-p`, JSON output), session resume and checkpointing;
   - sandboxing: seatbelt, docker or podman, and its network policy;
   - A2A support.
2. **Google Antigravity:**
   - what it is as of October 2026: the agent manager, the editor, the browser;
   - its agent's tools: terminal commands and their approval policy, file edits;
   - MCP support, and how it is configured;
   - rules, workflows and knowledge files;
   - any hooks or event triggers;
   - how an agent could be told to check an inbox without a human (scheduled or background agents? file watchers?);
   - which models it runs;
   - the limits on the AI Pro plan;
   - any CLI or API that drives it from outside.
3. **Other Google agent products with an API** (Jules, for example), briefly, if they offer a cleaner programmatic channel.
4. **For each surface:** can a Gemini agent RECEIVE a message from a hub (by push or by poll), SEND one, query shared state and hold a lock? What would still need a human?

End with a **recommended integration design for Gemini**, one for the CLI and one for Antigravity, ranked by robustness, and the experiments that would confirm it.
