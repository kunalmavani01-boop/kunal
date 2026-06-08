# Windows Release Checklist

This project is now moving toward a real Windows beta release instead of a source zip.

## Goal

Ship a browser-based Prompt Assistant beta that:

- opens without asking testers to install Python manually
- launches the local browser app automatically
- includes the app plus the tester docs in one clean Windows bundle

## Current lane

The Windows release lane is designed around:

- `release/PromptAssistantBeta.spec`
- `release/build_windows_exe.ps1`
- `project_360_degree_ai_prompt_assistant_platform.packaged_browser_launcher`

## Before building

1. Make sure the browser beta flow is the intended default release experience.
2. Install the release dependency set so `pyinstaller` is available.
3. Verify the app starts locally from source.
4. Verify the app still writes local data to `.prompt_assistant`.

## Build steps

1. Install the release extras.
2. Run `release/build_windows_exe.ps1`.
3. Check that `release-build/Prompt-Assistant-Beta-Windows` was created.

## Smoke test on Windows

Test on the same machine first:

1. Launch `PromptAssistantBeta.exe`.
2. Confirm the browser opens automatically.
3. Enter a rough prompt.
4. Confirm `Analyze Prompt` works.
5. Confirm the final prompt and alternates render.
6. Confirm library selection still works.
7. Confirm `.prompt_assistant` data is created locally.

Then test on a clean Windows machine:

1. Copy the whole `Prompt-Assistant-Beta-Windows` folder.
2. Launch `PromptAssistantBeta.exe`.
3. Repeat the same smoke test flow.

## Known blockers still outside this script

- `pyinstaller` is not installed yet in this workspace
- the release has not been tested on a clean Windows machine yet
- code signing is not configured
- there is no installer wrapper yet, only a portable release folder

## Go / no-go rule

Do not send the Windows beta broadly until:

- the executable starts on a clean machine
- the browser opens reliably
- the main prompt flow works end to end
- no manual Python install is required
