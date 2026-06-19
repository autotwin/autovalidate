# Add a New Fidelity Level

Autovalidate currently supports two fidelity levels:

| Level | Brain representation |
|-------|----------------------|
| `homogeneous` | Brain as a single tissue region |
| `heterogeneous` | Brain split into White Matter and Grey Matter |

This tutorial shows how to add a third level — **`detailed`** — which further separates the cerebellum and brainstem from the rest of the brain as distinct labels.

## Overview

Adding a fidelity level requires changes in three places:

1. A new `combine_labels_detailed` function in `combine_labels.py`
2. Dispatch in `run.py`
3. Validation in `autovalidate/config.py`

## Step 1 — Define the label constants

The `detailed` level needs to identify cerebellum and brainstem voxels from the segmentation output. Add constants to the relevant segmentation module. For SynthSeg (`autovalidate/segmentation/synthseg.py`):

```python
SYNTHSEG_CEREBELLUM_LABELS = [7, 8, 46, 47]   # cerebellar WM + GM (left + right)
SYNTHSEG_BRAINSTEM_LABELS  = [16]
```

Remove these labels from `SYNTHSEG_WM_LABELS` and `SYNTHSEG_GM_LABELS` so they are not double-counted.

## Step 2 — Write `combine_labels_detailed`

Open `autovalidate/combine/combine_labels.py` and add a new function:

```python
def combine_labels_detailed(
    wm: np.ndarray,
    gm: np.ndarray,
    csf: np.ndarray,
    skull: np.ndarray,
    cerebellum: np.ndarray,
    brainstem: np.ndarray,
    membranes: np.ndarray | None = None,
) -> np.ndarray:
    if not (wm.shape == gm.shape == csf.shape == skull.shape
            == cerebellum.shape == brainstem.shape):
        raise ValueError("All masks must have the same shape")

    if membranes is not None and membranes.shape != wm.shape:
        raise ValueError("All masks must have the same shape")

    mem = membranes if membranes is not None else np.zeros_like(wm)

    labels = np.zeros(wm.shape, dtype=np.uint8)
    labels[wm.astype(bool)]          = 1
    labels[gm.astype(bool)]          = 2
    labels[csf.astype(bool)]         = 3
    labels[skull.astype(bool)]       = 4
    labels[mem.astype(bool)]         = 5
    labels[cerebellum.astype(bool)]  = 6
    labels[brainstem.astype(bool)]   = 7
    return labels
```

## Step 3 — Register the fidelity name in `config.py`

In `autovalidate/config.py`, add `"detailed"` to the allowed set:

```python
brain_fidelity = raw_dict["run"]["brain_fidelity"].lower()
if brain_fidelity not in {"homogeneous", "heterogeneous", "detailed"}:   # ← add here
    raise ValueError("Wrong Fidelity Level! ...")
```

## Step 4 — Add dispatch in `run.py`

In the mask extraction step (step 5), extract the two new masks when the fidelity is `detailed`:

```python
if cfg.brain_fidelity == "detailed":
    cerebellum_mask = common.extract_mask(
        seg_output_file_data, synthseg.SYNTHSEG_CEREBELLUM_LABELS, False
    )
    brainstem_mask = common.extract_mask(
        seg_output_file_data, synthseg.SYNTHSEG_BRAINSTEM_LABELS, False
    )
```

In the combine step (step 9), add the new branch:

```python
elif cfg.brain_fidelity == "detailed":
    combined_labels = combine_labels.combine_labels_detailed(
        wm_mask, gm_mask, csf_mask, skull_mask,
        cerebellum_mask, brainstem_mask, membranes_mask
    )
```

## Step 5 — Update `config.toml`

```toml
[run]
brain_fidelity = "detailed"
```

## Label schema for the `detailed` level

| Label | Region |
|-------|--------|
| 0 | Background |
| 1 | White Matter |
| 2 | Grey Matter |
| 3 | CSF |
| 4 | Skull |
| 5 | Membranes (if enabled) |
| 6 | Cerebellum |
| 7 | Brainstem |

## Step 6 — Write tests

Add tests for `combine_labels_detailed` in `tests/test_combine_labels.py`, following the pattern of the existing homogeneous and heterogeneous tests. At minimum, verify:

- Cerebellum voxels are painted label 6
- Brainstem voxels are painted label 7
- No overlap between any two tissue masks

Run the suite:

```bash
python -m pytest tests/ -v
```
