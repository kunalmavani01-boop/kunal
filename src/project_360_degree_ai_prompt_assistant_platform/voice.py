"""Local microphone capture helpers for the desktop beta."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


VOICE_SCRIPT = r"""
Add-Type -AssemblyName System.Speech
$recognizers = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers()
if (-not $recognizers -or $recognizers.Count -eq 0) {
    @{ status = 'error'; message = 'No Windows speech recognizer is installed. Add an English speech pack in Windows settings first.' } | ConvertTo-Json -Compress
    exit 2
}
$culture = $recognizers[0].Culture
try {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($culture)
} catch {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
}
try {
    $recognizer.SetInputToDefaultAudioDevice()
} catch {
    @{ status = 'error'; message = 'Windows could not access the default microphone. Check microphone permission and your default input device.'; detail = $_.Exception.Message } | ConvertTo-Json -Compress
    exit 3
}
$recognizer.InitialSilenceTimeout = [TimeSpan]::FromSeconds(5)
$recognizer.BabbleTimeout = [TimeSpan]::FromSeconds(4)
$recognizer.EndSilenceTimeout = [TimeSpan]::FromMilliseconds(900)
$recognizer.EndSilenceTimeoutAmbiguous = [TimeSpan]::FromSeconds(1.4)
$recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
$result = $recognizer.Recognize([TimeSpan]::FromSeconds(%TIMEOUT%))
if ($result -and $result.Text) {
    @{ status = 'ok'; text = $result.Text; culture = $culture.Name } | ConvertTo-Json -Compress
} else {
    @{ status = 'empty'; message = 'No speech was recognized. Speak right after pressing Use Mic and confirm your microphone is set as the default input device.'; culture = $culture.Name } | ConvertTo-Json -Compress
}
"""


def transcribe_once(timeout_seconds: int = 12) -> str:
    script_text = VOICE_SCRIPT.replace("%TIMEOUT%", str(timeout_seconds))
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as handle:
        handle.write(script_text)
        script_path = Path(handle.name)

    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 6,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("The microphone timed out before anything was recognized.") from exc
    finally:
        script_path.unlink(missing_ok=True)

    if completed.returncode != 0:
        error_text = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(error_text or "Voice capture could not start.")

    raw_output = (completed.stdout or "").strip()
    if not raw_output:
        raise RuntimeError("Voice capture finished, but Windows did not return any speech.")

    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        return raw_output

    status = payload.get("status")
    if status == "ok":
        return str(payload.get("text", "")).strip()

    message = str(payload.get("message", "Voice capture could not start.")).strip()
    detail = str(payload.get("detail", "")).strip()
    if detail:
        message = f"{message}\n\n{detail}"
    raise RuntimeError(message)
