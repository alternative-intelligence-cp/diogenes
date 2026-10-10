# dio-r2b-antigravity-deep-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` (the context, and the author's two messages), then `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/out/dio-r2-gemini-antigravity-2026-10-10.md`, the first-round report on Gemini CLI and Antigravity.

**Your job: a deep second pass on Google Antigravity**, the author's intermediate target ("tie gemini in via antigravity"), filling the first report's gaps and UNVERIFIED claims. It mentions an Antigravity hooks file (`.agents/hooks.json`) with events such as `PreInvocation`, and an `injectSteps` output. Settle what those are.

Sources:
- antigravity.google and its documentation;
- Google's developer blogs and release notes;
- the Gemini CLI repository and documentation, where Antigravity shares components;
- reputable secondary write-ups, labelled as such.

Fetch large pages several times with narrow prompts, and quote where a design rests on the wording.

Settle each of these, or mark it UNVERIFIED and say what you tried:

1. **Hooks in Antigravity:**
   - the file, its location and scope (workspace or user);
   - every event and its payload;
   - what a hook may return (`injectSteps`, blocking, others);
   - whether a hook can feed text to the model;
   - whether hooks run sandboxed, and with what environment;
   - when this arrived, and how stable it is.
2. **MCP in Antigravity:** configuration, transports, whether an MCP tool can be called without the human approving each call, and whether a server can push notifications.
3. **Waking an agent without the human:**
   - scheduled tasks, background agents, the agent manager's API, file watchers, a CLI (`agy`?);
   - can anything start or resume an agent conversation from outside?
4. **The terminal and the sandbox:**
   - the command approval policy, and the allow and deny lists;
   - the network policy;
   - can an agent run a local CLI such as `dio`, and write to a directory outside its workspace?
5. **Identity:** does an agent conversation have a stable id or name that a hook or MCP server can read, so that a hub can address it?
6. **Limits on the Google AI Pro plan** that bear on running an agent that polls or is woken repeatedly.
7. **Gemini CLI, briefly, for contrast:** its hooks, MCP and headless mode, and whether it is the better way to run Gemini against a hub than Antigravity.

**End with** a recommended Antigravity integration for Diogenes, ranked by robustness. The author relays every Gemini alert by hand today, and the goal is to stop that. Add the experiments, with exact steps, that would confirm it.
