# dio-r1c-claude-code-mods-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` (the context, and the author's two messages) and `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-firsthand-2026-10-10.md`. Then read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/out/dio-r1b-claude-code-deep-2026-10-10.md`. It found that **Claude Code mods**, from 2.1.287 on, may be the best way to wake an idle session: a mod can spawn an unsandboxed long-poll process and call `$.prompt.submit`, which *"waits until the session is idle and then starts a new turn"*. They may also be a surface for the author.

**Your job: a deep, dated, sourced digest of Claude Code mods, as the basis for a "Diogenes mod".** Use the code.claude.com documentation: the pages r1b cites as mref, mapi and madm, plus anything they link to; the CHANGELOG at raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md; and the plugin documentation. Fetch large pages several times with narrow prompts. Quote where a design rests on the wording.

Settle each of these, or mark it UNVERIFIED and say what you tried:

1. **What a mod is.** Its file layout, how it is packaged (in a plugin? alone?), how it is installed and enabled per config directory, the language and runtime, and how it is versioned. How stable is the API: preview or stable, and how often has it changed in the changelog since 2.1.287?
2. **The events,** each with its payload and what a handler may return: `session.start`, `session.end`, `session.receive`, `session.send`, `session.measure`, `agent.spawn`, `prompt.autocomplete`, tool-call events, and any others.
3. **The API surface:**
   - `$.session` (`id()`, `usage()` and its rate-limit fields, name, model);
   - `$.prompt.submit` (its exact semantics while busy and while idle, `asUser`, how the turn is labelled to the model, any rate limits);
   - `$.process.spawn` (sandboxed or not, its lifetime, output handling, how it ends);
   - `$.ui` (panes, panels, status bands, toasts: what can be drawn, and where);
   - `$.store`, `$.fs`, `$.tool.register`, network access;
   - and anything else.
4. **Security and administration:**
   - the default guard (`sec-default`);
   - `allowManagedModsOnly`, and any other managed-settings controls;
   - what a Team or Enterprise Owner can enforce, and what a mod can and cannot do to the session's permissions;
   - `--safe-mode`;
   - how mod activity is shown to the user;
   - whether a mod can approve permissions or change settings. It should not.
5. **Headless and subagents:** do mods run under `claude -p`? Do they see subagents, and their `agent_id`s?
6. **Prior examples:** official or community mods that do messaging, inboxes, notifications or panels.

**End with a concrete design for a "Diogenes mod"**, with the exact events and API calls, covering:
- (a) a long-poll listener that wakes the session only when a message, a task or a lock event is addressed to it, with a short pointer and never the message text as the prompt;
- (b) a pane or status band showing unread messages, the roster, the leases held and each account's meters;
- (c) publishing context and rate-limit figures to the hub, given that the status line has no `rate_limits` on a Team seat;
- (d) mirroring `SendMessage` traffic into the audit log.

For each part, give the experiment that would confirm it, with exact steps, and what is UNVERIFIED.
