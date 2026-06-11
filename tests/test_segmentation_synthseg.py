from pathlib import Path

from autovalidate.segmentation.synthseg import create_synthseg_command

def test_create_synthseg_command():

    mri_synthseg_path = Path("dummy/path/to/mri_synthseg")
    t1_image_path = Path('dummy/t1_image.nii.gz')
    target_dir = Path("dummy/synthseg_output")

    command = create_synthseg_command(mri_synthseg_path, t1_image_path, target_dir)

    synthseg_output = target_dir / (Path(t1_image_path.stem).stem + "_SynthSeg.nii.gz")

    assert len(command) == 5
    assert command[0] == str(mri_synthseg_path)
    assert command[2] == str(t1_image_path)
    assert command[4] == str(synthseg_output)


