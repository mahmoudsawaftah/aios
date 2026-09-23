# Repair Antigravity Codex Agent

## Goal

Repair a blank `New Codex Agent` editor tab in Antigravity IDE when the OpenAI Codex sidebar still works.

## Confirm the failure

Check the newest Antigravity `renderer.log` and OpenAI `Codex.log`. This repair applies when the logs show both conditions:

- OpenAI cannot use `chatSessionsProvider`.
- After enabling the proposal, the renderer reports `depends on UNKNOWN service agentSessions`.

## Apply the repair

Run from the `aios` root:

```powershell
powershell -ExecutionPolicy Bypass -File .\execution\maint\fix-antigravity-codex-agent.ps1
```

The script:

1. Backs up Antigravity's installed `product.json` and `workbench.desktop.main.js`.
2. Allows the OpenAI extension's `chatSessionsProvider` and `languageModelProxy` proposals.
3. Restores the missing delayed singleton registration for `IAgentSessionsService`.
4. Validates the product JSON and JavaScript syntax.

Fully close and reopen Antigravity after the script succeeds.

## Verify

Open `New Codex Agent` and confirm the center editor renders. In the new logs, confirm these errors are absent:

- `CANNOT use API proposal: chatSessionsProvider`
- `depends on UNKNOWN service agentSessions`

## Restore

If Antigravity fails to start or the editor regresses, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\execution\maint\fix-antigravity-codex-agent.ps1 -Restore
```

Then fully restart Antigravity. Antigravity updates may replace the patched files; re-run diagnosis before reapplying the repair to a new version.
