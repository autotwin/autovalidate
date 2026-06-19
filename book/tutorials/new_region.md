# Add a New Tissue Region

This tutorial shows how to introduce an additional tissue label into the combined output. We use **cerebellum** as an example — splitting it out from the general brain/WM mask into its own label.

## Overview

Adding a region requires changes in three places:

1. Label constants in the relevant segmentation module(s)
2. `combine_labels.py` — assign the new label value
3. `run.py` — extract the new mask and pass it to the combine function

## Step 1 — Define label constants

In the segmentation module for the algorithm you are using, add a new constant for the cerebellum labels. For example, in `autovalidate/segmentation/synthseg.py`:

```python
SYNTHSEG_CEREBELLUM_LABELS = [7, 8, 46, 47]   # cerebellar WM + GM (left + right)
```

Then remove those same integers from `SYNTHSEG_WM_LABELS` and `SYNTHSEG_GM_LABELS` so the same voxels do not appear in two masks simultaneously.

Check the atlas documentation for your algorithm to identify the correct integer labels.

## Step 2 — Extract the mask in `run.py`

In the mask extraction step (step 5 of the pipeline), extract a cerebellum mask the same way as the other tissue masks:

```python
cerebellum_mask = common.extract_mask(
    seg_output_file_data, synthseg.SYNTHSEG_CEREBELLUM_LABELS, False
)
```

## Step 3 — Update `combine_labels.py`

Open `autovalidate/combine/combine_labels.py` and update `_assign_labels` to accept and paint the new region:

```python
def _assign_labels(wm, gm, csf, skull, membranes, cerebellum) -> np.ndarray:
    labels = np.zeros(wm.shape, dtype=np.uint8)
    labels[wm.astype(bool)]         = 1
    labels[gm.astype(bool)]         = 2
    labels[csf.astype(bool)]        = 3
    labels[skull.astype(bool)]      = 4
    labels[membranes.astype(bool)]  = 5
    labels[cerebellum.astype(bool)] = 6   # ← new label
    return labels
```

Update both `combine_labels_homogeneous` and `combine_labels_heterogeneous` to accept and forward the new argument.

## Step 4 — Wire it up in `run.py`

Pass `cerebellum_mask` when calling the combine function:

```python
combined_labels = combine_labels.combine_labels_homogeneous(
    brain_mask, csf_mask, skull_mask, membranes_mask, cerebellum_mask
)
```

## Label schema after the change

| Label | Region |
|-------|--------|
| 0 | Background |
| 1 | Brain (homogeneous) / White Matter (heterogeneous) |
| 2 | — / Grey Matter |
| 3 | CSF |
| 4 | Skull |
| 5 | Membranes (if enabled) |
| 6 | Cerebellum |

## Step 5 — Update tests

Add tests for:

- `_assign_labels` paints label 6 correctly
- Cerebellum voxels do not appear in WM or GM masks

Run the suite to confirm nothing is broken:

```bash
python -m pytest tests/ -v
```
