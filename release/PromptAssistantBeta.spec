# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path(SPECPATH).resolve().parent
src_root = project_root / "src"
entry_script = src_root / "project_360_degree_ai_prompt_assistant_platform" / "packaged_browser_launcher.py"

hiddenimports = [
    "project_360_degree_ai_prompt_assistant_platform.assistant",
    "project_360_degree_ai_prompt_assistant_platform.memory",
    "project_360_degree_ai_prompt_assistant_platform.optimizer",
    "project_360_degree_ai_prompt_assistant_platform.pack_catalog",
    "project_360_degree_ai_prompt_assistant_platform.prompt_library",
    "project_360_degree_ai_prompt_assistant_platform.providers",
    "project_360_degree_ai_prompt_assistant_platform.settings",
    "project_360_degree_ai_prompt_assistant_platform.web_ui",
]

datas = [
    (
        str(src_root / "project_360_degree_ai_prompt_assistant_platform" / "config" / "agents.yaml"),
        "project_360_degree_ai_prompt_assistant_platform/config",
    ),
    (
        str(src_root / "project_360_degree_ai_prompt_assistant_platform" / "config" / "tasks.yaml"),
        "project_360_degree_ai_prompt_assistant_platform/config",
    ),
    (
        str(src_root / "project_360_degree_ai_prompt_assistant_platform" / "data" / "open_source_prompt_seed.json"),
        "project_360_degree_ai_prompt_assistant_platform/data",
    ),
]


a = Analysis(
    [str(entry_script)],
    pathex=[str(src_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PromptAssistantBeta",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PromptAssistantBeta",
)
