import sys, types, pathlib

# --- Mock mínimo do módulo bpy para testes unitários ---
def _mock_bpy():
    mock = types.ModuleType("bpy")
    mock.context = types.SimpleNamespace(scene=types.SimpleNamespace(
        sequence_editor=None,
        sequence_editor_create=lambda: None,
    ))
    class _Movie:
        frame_duration = 24
    mock.data = types.SimpleNamespace(movieclips=types.SimpleNamespace(
        load=lambda path: _Movie()
    ))
    sys.modules["bpy"] = mock

_mock_bpy()

# --- Fixture: diretório raiz do projeto ---
import pytest, os

@pytest.fixture(scope="session")
def project_root():
    return pathlib.Path(__file__).resolve().parents[1]

# --- Fixture para gerar mini assets de vídeo e áudio ---

@pytest.fixture(scope="session", autouse=True)
def prepare_assets(project_root):
    assets = project_root / "tests" / "integration" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    video = assets / "video.mp4"
    audio = assets / "audio.wav"
    if not video.exists():
        with open(video, "wb") as f:
            f.write(b"\x00")
    if not audio.exists():
        with open(audio, "wb") as f:
            f.write(b"\x00")
    return assets
