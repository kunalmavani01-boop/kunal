# PROMPTER

PROMPTER is a local-first browser app with two core actions:

1. `Refine Prompt`
2. `Open Prompt Library`

The goal is simple:

- turn a rough prompt into a stronger final prompt
- show more efficient prompt versions that help reduce wasted tokens
- help users find ready-made prompts quickly from one unified library

## What PROMPTER Does

The browser MVP focuses on one clear flow:

1. paste a rough prompt or idea
2. click `Refine Prompt`
3. get a final prompt plus alternate versions
4. optionally open the prompt library and adapt a ready-made prompt

The app currently includes:

- a browser-first local UI
- prompt refinement with a final prompt output
- approximate token-efficiency comparison
- a unified prompt library
- category-based library browsing
- top prompt matches inside each category
- local prompt history
- bundled open-source prompt references

## Quick Feature Brief

- `Refine Prompt`: clean up a rough prompt, make it clearer, and reduce ambiguity
- `Prompt Library`: choose a category, see the strongest prompt matches, then use or adapt one
- `Token Saving`: compare prompt versions and pick the one that is likely to use fewer tokens
- `Light Cleanup`: common typo and rough-format cleanup support before prompt rebuilding

## Download And Run

### 1. Download the project

Download or clone this repository to your computer.

### 2. Open the app on Windows

Double-click:

`PROMPTER.bat`

If you prefer, you can also use:

`start_prompt_assistant.bat`

This opens the browser MVP directly in your local browser.

Keep the launcher window open while the app is running. The app will also
write its active local link to:

`.\.prompt_assistant\current_url.txt`

### 3. Optional command line launch

From the project folder:

```bash
prompt_assistant web
```

## Main User Flows

### 1. Refine Prompt

Use this when the user already has a rough prompt.

The app:

- analyzes the prompt
- improves structure
- reduces ambiguity
- shows a final prompt
- shows alternate prompt versions such as:
  - most efficient
  - balanced
  - deeper reasoning

### 2. Open Prompt Library

Use this when the user wants a strong starting point from the library.

The intended MVP experience is:

1. choose a category
2. see the top matching prompts
3. choose one prompt
4. either use it directly or adapt it to the user's need

## Why It Saves Tokens

PROMPTER helps save cost by reducing ambiguity and retries:

- clearer prompts mean fewer back-and-forth correction turns
- structured prompt options reduce wasted output
- token-efficiency hints help users choose a leaner version when needed

It is not only about shorter prompts. It is about getting to a usable result faster.

## Build A Windows Beta

The project includes a Windows packaging script for a portable `.exe` build:

```powershell
powershell -ExecutionPolicy Bypass -File .\release\build_windows_exe.ps1
```

Then open the newest packaged build from the latest folder inside:

`release-build\`

For normal MVP use during development, the main launch path is:

`start_prompt_assistant.bat`

## Project Layout

```text
src/project_360_degree_ai_prompt_assistant_platform/
  assistant.py
  main.py
  optimizer.py
  prompt_library.py
  web_ui.py
  settings.py

release/
  build_windows_exe.ps1
  PromptAssistantBeta.spec

tests/
```

## Notes

- The browser MVP is the main product path.
- The product-facing name is `PROMPTER`.
- The old CrewAI scaffold is still in the codebase, but it is not the main user experience.
- The desktop runtime path is not the primary MVP path.
- Future work may add a hybrid retrieval layer, but the current MVP stays local-first.
