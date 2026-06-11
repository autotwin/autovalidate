from autovalidate.io.filename_builder import filename_building

def test_filename_building_combined(tmp_path):

    subject_id = "sub001"
    motion_type = "NR"
    algorithm = "synthseg"
    brain_fidelity = "homogeneous"
    membranes = True
    mask_type = "combined"

    filename = filename_building(subject_id, motion_type, algorithm, brain_fidelity, membranes, mask_type)

    assert str(filename) == "sub001-NR-synthseg-homogeneous-membranesON-combined.npy"

def test_filename_building_specific_mask(tmp_path):

    subject_id = "sub001"
    motion_type = "NE"
    algorithm = "synthseg"
    brain_fidelity = "heterogeneous"
    membranes = False
    mask_type = "wm"

    filename = filename_building(subject_id, motion_type, algorithm, brain_fidelity, membranes, mask_type)

    assert str(filename) == "sub001-NE-synthseg-heterogeneous-membranesOFF-wm.nii.gz"