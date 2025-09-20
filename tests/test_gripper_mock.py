import sys
import importlib
from types import SimpleNamespace

class FakeDobot:
    """A minimal fake Dobot used for testing. Records commands and keeps the last instance."""
    last = None

    def __init__(self, port=None):
        FakeDobot.last = self
        self.port = port
        self.commands = []

    def speed(self, v, a):
        self.commands.append(('speed', v, a))

    def home(self):
        self.commands.append(('home',))

    def move_to(self, mode=0, **pt):
        self.commands.append(('move_to', mode, pt))

    def suck(self, state):
        self.commands.append(('suck', state))

    def close(self):
        self.commands.append(('close',))


def test_gripper_sequence_runs_quiet(monkeypatch):
    # Force argv to a safe dry-run set of arguments (no waits, no real port)
    monkeypatch.setattr(sys, 'argv', [
        'lab2_gripper_multi.py',
        '--port', '/dev/null',
        '--hover', '10',
        '--v', '500',
        '--a', '500',
        '--close_dwell', '0',
        '--open_dwell', '0',
        '--hold', '0',
    ])

    # Ensure we import a fresh copy of the module
    if 'lab2_gripper_multi' in sys.modules:
        importlib.reload(sys.modules['lab2_gripper_multi'])
    mod = importlib.import_module('lab2_gripper_multi')

    # Monkeypatch the Dobot implementation used by the module to our fake
    monkeypatch.setattr(mod, 'dobot_mod', SimpleNamespace(Dobot=FakeDobot))
    # Ensure MODE_PTP provides MOVJ_XYZ used as default in the module
    monkeypatch.setattr(mod, 'MODE_PTP', SimpleNamespace(MOVJ_XYZ=1))

    # Run main() - should complete without touching real hardware
    mod.main()

    # Inspect the last FakeDobot instance recorded
    inst = FakeDobot.last
    assert inst is not None, "FakeDobot was not instantiated"

    # Basic sanity checks: speed, home and at least a few move_to/suck calls occurred
    cmds = [c[0] for c in inst.commands]
    assert 'speed' in cmds
    assert 'home' in cmds
    assert any(c == 'move_to' for c in cmds)
    assert any(c == 'suck' for c in cmds)