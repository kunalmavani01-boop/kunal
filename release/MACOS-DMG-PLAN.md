# macOS DMG Plan

This project cannot produce a trustworthy `.dmg` directly from the current Windows workspace.

## Honest status

The browser beta can become a Mac release, but it still needs a macOS build environment.

## What the Mac lane should ship

- a `.app` bundle that launches the local browser beta
- a `.dmg` wrapper for testers
- clear first-run instructions if Gatekeeper blocks an unsigned beta

## What is required

1. A macOS machine or macOS CI runner
2. A matching Python release environment on macOS
3. A packaging tool path such as PyInstaller on macOS
4. Optional but recommended:
   - Developer ID signing
   - notarization

## Practical release path

### Phase 1: Unsigned internal Mac beta

Use a Mac build environment to:

1. install the project
2. install the release packaging dependency
3. build a `.app`
4. wrap the `.app` in a simple `.dmg`
5. test on a second Mac if possible

This is the fastest path for trusted friends-and-family testing.

### Phase 2: Cleaner public-facing Mac beta

Add:

1. signing
2. notarization
3. branded disk image
4. clearer first-run experience

## What to test on macOS

1. Double-click launch from Finder
2. Browser opens automatically
3. Prompt analysis works
4. Final prompt output works
5. Local storage remains local
6. The app can be reopened after closing

## Current blocker list

- no Mac build machine in this workspace
- no macOS packaging script tested yet
- no signing or notarization setup
- no clean-machine Mac verification yet

## Recommendation

Finish the Windows `.exe` lane first.

Only move to `.dmg` once:

- the browser beta flow is stable
- the Windows portable release works on a clean machine
- a real Mac build environment is available
