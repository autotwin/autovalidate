# Brain Fidelity

Brain fidelity controls how much anatomical detail is preserved in the label map. It determines whether white matter and grey matter are treated as separate regions or merged into a single brain label.

## Homogeneous

All brain tissue (white matter + grey matter) is assigned a single label (`1 = Brain`). The brain is treated as a uniform material.

```
Label 0 — Background
Label 1 — Brain (WM + GM combined)
Label 3 — CSF
Label 4 — Skull
Label 5 — Membranes (if enabled)
```

Use homogeneous when:
- You want a simpler model with fewer material properties to define
- Computational cost is a concern
- The distinction between WM and GM is not critical for your simulation

## Heterogeneous

White matter and grey matter are assigned separate labels (`1 = WM`, `2 = GM`). Each tissue can have its own material properties in simulation.

```
Label 0 — Background
Label 1 — White Matter
Label 2 — Gray Matter
Label 3 — CSF
Label 4 — Skull
Label 5 — Membranes (if enabled)
```

Use heterogeneous when:
- Your material model distinguishes between WM and GM mechanical properties
- Higher anatomical fidelity is required

## Config

```toml
[run]
brain_fidelity = "homogeneous"  # homogeneous / heterogeneous
```

> **Note:** SLANT and SynthSeg provide enough label detail to support both fidelity levels. FSL FAST also supports both since it produces separate CSF, GM, and WM tissue classes.
