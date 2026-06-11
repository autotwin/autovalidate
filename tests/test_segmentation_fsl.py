from pathlib import Path

from autovalidate.segmentation.fsl import create_bet_command, create_fast_command


def test_create_bet_command():

    bet_path      = Path("/usr/local/fsl/bin/bet")
    t1_path       = Path("dummy/path/to/t1.nii.gz")
    output_prefix = Path("dummy/output/brain")

    cmd = create_bet_command(bet_path, t1_path, output_prefix)

    assert cmd[0] == str(bet_path)
    assert str(t1_path)       in cmd
    assert str(output_prefix) in cmd
    assert "-R" in cmd
    assert "-f" in cmd
    assert "-m" in cmd


def test_create_fast_command():

    fast_path     = Path("/usr/local/fsl/bin/fast")
    brain_path    = Path("dummy/output/brain.nii.gz")
    output_prefix = Path("dummy/output/fast")

    cmd = create_fast_command(fast_path, brain_path, output_prefix)

    assert cmd[0] == str(fast_path)
    assert str(brain_path)    in cmd
    assert str(output_prefix) in cmd
    assert "-o" in cmd
