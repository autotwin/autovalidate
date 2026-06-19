# Bring Your Own Algorithm

This tutorial shows how to add a new segmentation algorithm to Autovalidate. We use a fictional algorithm called **MyAlgo** as an example.

## Overview

Adding an algorithm requires changes in four places:

1. A new module in `autovalidate/segmentation/`
2. Label constants for tissue types
3. Dispatch in `run.py`
4. Validation in `autovalidate/config.py`

## Step 1 — Create the segmentation module

Create `autovalidate/segmentation/myalgo.py`:

```python
from pathlib import Path

MYALGO_CSF_LABELS            = [10, 11, 12]
MYALGO_WM_LABELS             = [1, 2]
MYALGO_GM_LABELS             = [3, 4, 5, 6, 7, 8]
MYALGO_BRAIN_EXCLUDE_LABELS  = [0, 10, 11, 12]   # background + CSF

def create_myalgo_command(binary_path: Path, t1_path: Path, output_dir: Path) -> list:
    out = output_dir / (t1_path.stem.replace(".nii", "") + "_MyAlgo.nii.gz")
    return [str(binary_path), "--input", str(t1_path), "--output", str(out)]
```

The four label lists follow the same convention used by every algorithm:

| Constant | Meaning |
|----------|---------|
| `BRAIN_EXCLUDE_LABELS` | Background + CSF — everything that is *not* brain tissue |
| `CSF_LABELS` | Ventricular and subarachnoid CSF |
| `WM_LABELS` | White matter regions |
| `GM_LABELS` | Cortical and subcortical grey matter |

## Step 2 — Register the algorithm name

In `autovalidate/config.py`, add `"myalgo"` to the allowed set and add the tool path field:

```python
# In parse_config:
algorithm = raw_dict["run"]["algorithm"].lower()
if algorithm not in {"synthseg", "fsl", "slant", "myalgo"}:   # ← add here
    raise ValueError("Wrong Segmentation Algorithm! ...")

if algorithm == "myalgo":
    if "myalgo" not in raw_dict["env"]:
        raise ValueError("myalgo binary path not specified!")
```

Add `myalgo: str | None` to the `Config` dataclass and populate it in `parse_config`:

```python
myalgo = raw_dict["env"].get("myalgo"),
```

## Step 3 — Add dispatch in `run.py`

Import the new module at the top of `run.py`:

```python
from autovalidate.segmentation import myalgo
```

In the segmentation step (step 4 of the pipeline), add an `elif` branch:

```python
elif algorithm == "myalgo":
    myalgo_path = Path(cfg.myalgo)
    t1_path = Path(path_dict["t1"])
    cmd = myalgo.create_myalgo_command(myalgo_path, t1_path, tmp_dir)
    subprocess.run(cmd, check=True)
    seg_out = tmp_dir / (t1_path.stem.replace(".nii", "") + "_MyAlgo.nii.gz")
    seg_output_file_data, seg_output_file_affine = nifti_io.load_nifti(seg_out)
```

In the mask extraction step (step 5):

```python
elif algorithm == "myalgo":
    brain_mask = common.extract_mask(seg_output_file_data, myalgo.MYALGO_BRAIN_EXCLUDE_LABELS, True)
    csf_mask   = common.extract_mask(seg_output_file_data, myalgo.MYALGO_CSF_LABELS,           False)
    wm_mask    = common.extract_mask(seg_output_file_data, myalgo.MYALGO_WM_LABELS,            False)
    gm_mask    = common.extract_mask(seg_output_file_data, myalgo.MYALGO_GM_LABELS,            False)
```

## Step 4 — Add a config entry

In your `config.toml`:

```toml
[env]
myalgo = "/path/to/myalgo/bin/myalgo"

[run]
algorithm = "myalgo"
```

## Step 5 — Write tests

Add `tests/test_myalgo.py` following the pattern of the existing segmentation tests. At minimum, test:

- `create_myalgo_command` returns the correct list structure
- Label constants are non-empty and have no unexpected overlap

Run the suite to confirm nothing is broken:

```bash
python -m pytest tests/ -v
```
