
import sys, types, pathlib, subprocess, wave


# --- Mock mínimo do módulo bpy para testes unitários ---
def _mock_bpy():
    mock = types.ModuleType("bpy")
    mock.types = types.SimpleNamespace(Sequence=type("Sequence", (), {}))


    def _make_strip(**kw):
        strip = types.SimpleNamespace(**kw)
        strip.frame_final_start = kw.get("frame_start", 1)
        strip.frame_final_end = kw.get("frame_end", strip.frame_final_start)
        strip.select = False
        return strip

    class SeqList(list):
        def get(self, name):
            return next((s for s in self if getattr(s, "name", None) == name), None)

    sequences_all = SeqList()

    selected_sequences = SeqList()
    seq_editor = types.SimpleNamespace(
        sequences=types.SimpleNamespace(
            new_movie=lambda **k: sequences_all.append(_make_strip(**k)) or sequences_all[-1],
            new_sound=lambda **k: sequences_all.append(_make_strip(**k)) or sequences_all[-1],
            new_image=lambda **k: sequences_all.append(_make_strip(**k)) or sequences_all[-1],
            new_effect=lambda **k: sequences_all.append(_make_strip(**k)) or sequences_all[-1],
        ),
        sequences_all=sequences_all,
    )

    scene = types.SimpleNamespace(
        sequence_editor=None,
        sequence_editor_create=lambda: setattr(scene, "sequence_editor", seq_editor),
        render=types.SimpleNamespace(),
        frame_current=1,
    )
    mock.context = types.SimpleNamespace(scene=scene, selected_sequences=selected_sequences)

    class _Movie:
        frame_duration = 24

    mock.data = types.SimpleNamespace(movieclips=types.SimpleNamespace(
        load=lambda path: _Movie(),
        remove=lambda x: None,
    ))

    def _op_add(**kw):
        strip = _make_strip(**kw)
        sequences_all.append(strip)
        selected_sequences.clear()
        selected_sequences.append(strip)
        return strip

    mock.ops = types.ModuleType("ops")
    mock.ops.sequencer = types.SimpleNamespace(
        select_all=lambda action=None: None,
        delete=lambda: None,
        split=lambda frame=None, side=None, use_cursor_position=False: None,
        meta_make=lambda: None,
        movie_strip_add=lambda filepath=None, frame_start=1, channel=1, overlap=False: _op_add(filepath=filepath, frame_start=frame_start, channel=channel),
        image_strip_add=lambda filepath=None, frame_start=1, channel=1, overlap=False: _op_add(filepath=filepath, frame_start=frame_start, channel=channel),
        sound_strip_add=lambda filepath=None, frame_start=1, channel=1, overlap=False: _op_add(filepath=filepath, frame_start=frame_start, channel=channel),
    )
    mock.ops.render = types.SimpleNamespace(render=lambda animation=True: None)

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
        video.write_bytes(b"\x00")
    if not audio.exists():
        with wave.open(str(audio), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            w.writeframes(b"\x00\x00" * 44100)
    return assets


@pytest.fixture
def strip_factory():
    def _factory(name="strip", channel=1, frame_start=1, length=10):
        return types.SimpleNamespace(
            name=name,
            channel=channel,
            frame_start=frame_start,
            frame_final_start=frame_start,
            frame_final_end=frame_start + length,
            select=False,
        )

    return _factory
