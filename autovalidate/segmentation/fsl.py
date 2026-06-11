from pathlib import Path

FSL_BRAIN_EXCLUDE_LABELS = [0]
FSL_CSF_LABELS           = [1]
FSL_GM_LABELS            = [2]
FSL_WM_LABELS            = [3]


def create_bet_command(bet_path: Path, t1_path: Path, output_prefix: Path, fractional_intensity: float = 0.3) -> list:
    return [
        str(bet_path),
        str(t1_path),
        str(output_prefix),
        "-R",
        "-f", str(fractional_intensity),
        "-m",
    ]


def create_fast_command(fast_path: Path, brain_path: Path, output_prefix: Path) -> list:
    return [
        str(fast_path),
        "-t", "1",
        "-n", "3",
        "-H", "0.1",
        "-I", "4",
        "-l", "20",
        "-o", str(output_prefix),
        str(brain_path),
    ]
