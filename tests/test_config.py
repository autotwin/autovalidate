import pytest

from autovalidate.config import parse_config

def test_parse_config():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "synthseg",
          "brain_fidelity":    "heterogeneous",
          "include_membranes": True,
          }
        }

    config_class = parse_config(raw_lines)

    assert config_class.mri_synthseg == "/dummy/mri_synthseg"
    assert config_class.mri_convert == "/dummy/mri_convert"
    assert config_class.subject_dir == "/dummy/subject"
    assert config_class.output_dir == "/dummy/output"
    assert config_class.subject_id == "U01_HJF_0001_01"
    assert config_class.motion_type == "NR"
    assert config_class.algorithm == "synthseg"
    assert config_class.brain_fidelity == "heterogeneous"
    assert config_class.include_membranes == True

def test_parse_config_missing_env():

    raw_lines = {
          "run": {
          "subject_dir":       "/dummy/subject",                
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "algorithm":         "synthseg",                      
          "brain_fidelity":    "heterogeneous",
          "include_membranes": True,
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_run():

    raw_lines = {
          "env": {    
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_subject_dir():

    raw_lines = {
          "env": {    
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {                
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "algorithm":         "synthseg",                      
          "brain_fidelity":    "heterogeneous",
          "include_membranes": True,
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_output_dir():

    raw_lines = {
          "env": {    
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {                
          "subject_dir":       "/dummy/subject",
          "subject_id":        "U01_HJF_0001_01",  
          "algorithm":         "synthseg",                      
          "brain_fidelity":    "heterogeneous",
          "include_membranes": True,
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_subject_id():

    raw_lines = {
          "env": {    
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {                
          "subject_dir":       "/dummy/subject",  
          "algorithm":         "synthseg",                      
          "brain_fidelity":    "heterogeneous",
          "include_membranes": True,
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_wrong_algorithm_value():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "samseg",
          "brain_fidelity":    "heterogeneous",
          "include_membranes": True,
          }
        }

    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_wrong_fidelity_value():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "synthseg",
          "brain_fidelity":    "medium",
          "include_membranes": True,
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_wrong_membranes_value():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "synthseg",
          "brain_fidelity":    "homogeneous",
          "include_membranes": "yes",
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_synthseg_value():

    raw_lines = {
          "env": {
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "synthseg",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          }
        }
    
    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_fsl_value():

    raw_lines = {
          "env": {
          # bet and fast deliberately absent
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "fsl",
          "brain_fidelity":    "homogeneous",
          "include_membranes": False,
          }
        }

    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_convert_value():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "synthseg",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          }
        }

    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_missing_motion_type():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "algorithm":         "synthseg",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          }
        }

    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)

def test_parse_config_fsl_stores_bet_fast_paths():

    raw_lines = {
          "env": {
          "bet":  "/usr/local/fsl/bin/bet",
          "fast": "/usr/local/fsl/bin/fast",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "fsl",
          "brain_fidelity":    "homogeneous",
          "include_membranes": False,
          }
        }

    cfg = parse_config(raw_lines)

    assert cfg.bet  == "/usr/local/fsl/bin/bet"
    assert cfg.fast == "/usr/local/fsl/bin/fast"


def test_parse_config_fsl_missing_fast_raises():

    raw_lines = {
          "env": {
          "bet": "/usr/local/fsl/bin/bet",
          # fast deliberately absent
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "fsl",
          "brain_fidelity":    "homogeneous",
          "include_membranes": False,
          }
        }

    with pytest.raises(ValueError):
        parse_config(raw_lines)


def test_parse_config_fsl_membranes_requires_mri_convert():

    raw_lines = {
          "env": {
          "bet":  "/usr/local/fsl/bin/bet",
          "fast": "/usr/local/fsl/bin/fast",
          # mri_convert deliberately absent
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "fsl",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          }
        }

    with pytest.raises(ValueError):
        parse_config(raw_lines)


def test_parse_config_fsl_membranes_stores_mri_convert():

    raw_lines = {
          "env": {
          "bet":         "/usr/local/fsl/bin/bet",
          "fast":        "/usr/local/fsl/bin/fast",
          "mri_convert": "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "fsl",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          }
        }

    cfg = parse_config(raw_lines)

    assert cfg.mri_convert == "/dummy/mri_convert"


def test_parse_config_wrong_motion_type_value():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "XY",
          "algorithm":         "synthseg",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          }
        }

    with pytest.raises(ValueError):
        config_class = parse_config(raw_lines)


def test_parse_config_keep_intermediate_files_defaults_false():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":       "/dummy/subject",
          "output_dir":        "/dummy/output",
          "subject_id":        "U01_HJF_0001_01",
          "motion_type":       "NR",
          "algorithm":         "synthseg",
          "brain_fidelity":    "homogeneous",
          "include_membranes": True,
          # keep_intermediate_files deliberately absent
          }
        }

    cfg = parse_config(raw_lines)

    assert cfg.keep_intermediate_files == False


def test_parse_config_keep_intermediate_files_true():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":             "/dummy/subject",
          "output_dir":              "/dummy/output",
          "subject_id":              "U01_HJF_0001_01",
          "motion_type":             "NR",
          "algorithm":               "synthseg",
          "brain_fidelity":          "homogeneous",
          "include_membranes":       True,
          "keep_intermediate_files": True,
          }
        }

    cfg = parse_config(raw_lines)

    assert cfg.keep_intermediate_files == True


def test_parse_config_keep_intermediate_files_wrong_value():

    raw_lines = {
          "env": {
          "mri_synthseg": "/dummy/mri_synthseg",
          "mri_convert":  "/dummy/mri_convert",
          },
          "run": {
          "subject_dir":             "/dummy/subject",
          "output_dir":              "/dummy/output",
          "subject_id":              "U01_HJF_0001_01",
          "motion_type":             "NR",
          "algorithm":               "synthseg",
          "brain_fidelity":          "homogeneous",
          "include_membranes":       True,
          "keep_intermediate_files": "yes",
          }
        }

    with pytest.raises(ValueError):
        parse_config(raw_lines)
