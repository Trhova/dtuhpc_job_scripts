#!/usr/bin/env python3
"""
Summarise kneaddata read statistics across samples.

For each sample directory under the kneaddata output root this script parses
the corresponding kneaddata log, extracts read counts (raw, host, non-host,
final paired outputs), writes a CSV summary, prints a concise table, and
optionally generates a stacked bar plot showing host contamination versus
remaining reads.

Example:
    python kneaddata_read_summary.py \
        --kneaddata-root /work3/trhova/kneaddata_project/metagenomics_80/kneaddata_output \
        --output-dir /work3/trhova/kneaddata_project/metagenomics_80
"""

from __future__ import annotations

import argparse
import csv
import re
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

in_ipython = "ipykernel" in sys.modules or "IPython" in sys.modules
display_available = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

try:
    import matplotlib

    if not in_ipython and not display_available and "MPLBACKEND" not in os.environ:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - optional dependency
    plt = None


@dataclass
class SampleMetrics:
    sample: str
    total_reads: Optional[int] = None
    host_paired_reads: int = 0
    host_orphan1_reads: int = 0
    host_orphan2_reads: int = 0
    final_paired_1_reads: Optional[int] = None
    final_paired_2_reads: Optional[int] = None
    host_reads: Optional[int] = field(init=False, default=None)
    non_host_reads: Optional[int] = field(init=False, default=None)
    host_fraction: Optional[float] = field(init=False, default=None)

    def finalize(self) -> None:
        """Derive aggregate metrics once raw counts are populated."""
        self.host_reads = max(
            self.host_paired_reads + self.host_orphan1_reads + self.host_orphan2_reads,
            0,
        )
        if self.total_reads is not None:
            self.non_host_reads = max(self.total_reads - self.host_reads, 0)
            if self.total_reads > 0:
                self.host_fraction = self.host_reads / self.total_reads


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate kneaddata read statistics and plot host contamination."
    )
    parser.add_argument(
        "--kneaddata-root",
        type=Path,
        default=Path("/work3/trhova/kneaddata_project/metagenomics_80/kneaddata_output"),
        help="Root directory containing per-sample kneaddata folders.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory where the CSV summary and plot will be written. "
            "Defaults to the kneaddata root."
        ),
    )
    parser.add_argument(
        "--csv-name",
        default="kneaddata_read_summary.csv",
        help="Filename for the output CSV (written inside output-dir).",
    )
    parser.add_argument(
        "--plot-name",
        default="kneaddata_host_contamination.png",
        help="Filename for the stacked bar plot (written inside output-dir).",
    )
    parser.add_argument(
        "--plot-mode",
        choices=("auto", "show", "save", "none"),
        default="auto",
        help=(
            "Plot behaviour: 'auto' shows in notebooks and saves elsewhere; "
            "'show' displays inline; 'save' writes to disk; 'none' skips plotting."
        ),
    )
    args, _ = parser.parse_known_args()
    return args


def extract_terminal_number(line: str) -> Optional[int]:
    """Return the final numeric value in a log line as an integer."""
    maybe_value = line.strip().split(":")[-1].strip()
    try:
        if maybe_value.endswith("%"):
            maybe_value = maybe_value[:-1]
        return int(float(maybe_value))
    except ValueError:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", line)
        if match:
            return int(float(match.group(1)))
    return None


def parse_kneaddata_log(log_path: Path) -> SampleMetrics:
    """Extract per-sample metrics from a kneaddata log file."""
    sample_name = log_path.parent.name
    metrics = SampleMetrics(sample=sample_name)

    with log_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if "READ COUNT: raw pair1" in line:
                value = extract_terminal_number(line)
                if value is not None:
                    metrics.total_reads = value
            elif "Total contaminate sequences in file" in line:
                value = extract_terminal_number(line)
                if value is None:
                    continue
                if "_paired_contam_1.fastq" in line:
                    metrics.host_paired_reads = value
                elif "_unmatched_1_contam.fastq" in line:
                    metrics.host_orphan1_reads = value
                elif "_unmatched_2_contam.fastq" in line:
                    metrics.host_orphan2_reads = value
            elif "READ COUNT: final pair1" in line:
                value = extract_terminal_number(line)
                if value is not None:
                    metrics.final_paired_1_reads = value
            elif "READ COUNT: final pair2" in line:
                value = extract_terminal_number(line)
                if value is not None:
                    metrics.final_paired_2_reads = value

    metrics.finalize()
    return metrics


def iter_sample_logs(root: Path) -> Iterable[Path]:
    """Yield kneaddata log files under each immediate child directory."""
    if not root.exists():
        raise FileNotFoundError(f"Kneaddata root not found: {root}")

    for sample_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        log_files = sorted(sample_dir.glob("*_kneaddata.log"))
        if not log_files:
            continue
        yield log_files[0]


def write_csv(metrics: List[SampleMetrics], csv_path: Path) -> None:
    """Persist metrics to CSV."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample",
        "total_reads",
        "host_reads",
        "non_host_reads",
        "final_paired_1_reads",
        "final_paired_2_reads",
        "host_paired_reads",
        "host_orphan1_reads",
        "host_orphan2_reads",
        "host_fraction",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for metric in metrics:
            writer.writerow(
                {
                    "sample": metric.sample,
                    "total_reads": metric.total_reads,
                    "host_reads": metric.host_reads,
                    "non_host_reads": metric.non_host_reads,
                    "final_paired_1_reads": metric.final_paired_1_reads,
                    "final_paired_2_reads": metric.final_paired_2_reads,
                    "host_paired_reads": metric.host_paired_reads,
                    "host_orphan1_reads": metric.host_orphan1_reads,
                    "host_orphan2_reads": metric.host_orphan2_reads,
                    "host_fraction": (
                        f"{metric.host_fraction:.4f}" if metric.host_fraction is not None else ""
                    ),
                }
            )


def print_table(metrics: List[SampleMetrics]) -> None:
    """Emit a simple aligned table to stdout."""
    columns = [
        ("Sample", "sample"),
        ("Total", "total_reads"),
        ("Host", "host_reads"),
        ("Non-host", "non_host_reads"),
        ("Final pair1", "final_paired_1_reads"),
        ("Final pair2", "final_paired_2_reads"),
        ("Host %", "host_fraction"),
    ]
    # Compute column widths based on stringified values
    rows = []
    for metric in metrics:
        row = []
        for _, attr in columns:
            value = getattr(metric, attr)
            if attr == "host_fraction":
                row.append(f"{value*100:.2f}%" if value is not None else "NA")
            elif value is None:
                row.append("NA")
            elif isinstance(value, (int, float)):
                if isinstance(value, float) and not value.is_integer():
                    row.append(f"{value:,.2f}")
                else:
                    row.append(f"{int(value):,}")
            else:
                row.append(str(value))
        rows.append(row)

    widths = []
    for idx, (header, _) in enumerate(columns):
        col_items = [row[idx] for row in rows] if rows else []
        widths.append(max(len(header), *(len(item) for item in col_items)))

    header_line = " | ".join(
        header.ljust(width) for width, (header, _) in zip(widths, columns)
    )
    separator = "-+-".join("-" * width for width in widths)
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(item.ljust(width) for item, width in zip(row, widths)))


def resolve_plot_mode(mode: str) -> str:
    """Resolve plotting mode to concrete behaviour."""
    if mode == "auto":
        mode = "show" if in_ipython else "save"
    return mode


def plot_host_contamination(
    metrics: List[SampleMetrics], plot_path: Path, mode: str = "save"
) -> Optional[Path]:
    """Generate stacked bar plot of host vs remaining reads."""
    if not metrics or plt is None:
        return None

    samples = [m.sample for m in metrics if m.total_reads is not None]
    host = [m.host_reads or 0 for m in metrics if m.total_reads is not None]
    non_host = [
        max((m.total_reads or 0) - (m.host_reads or 0), 0)
        for m in metrics
        if m.total_reads is not None
    ]

    if not samples:
        return

    fig, ax = plt.subplots(figsize=(max(8, len(samples) * 0.4), 6))
    ax.bar(samples, non_host, label="Remaining reads", color="#4C72B0")
    ax.bar(samples, host, bottom=non_host, label="Host contamination", color="#DD8452")
    ax.set_ylabel("Read count")
    ax.set_title("Host contamination versus total reads (kneaddata)")
    ax.legend()
    ax.tick_params(axis="x", labelrotation=45)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    if mode == "none":
        plt.close(fig)
        return None

    if mode == "show":
        plt.show()
        plt.close(fig)
        return None

    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    return plot_path


def main() -> None:
    args = parse_args()
    kneaddata_root: Path = args.kneaddata_root
    output_dir: Path = args.output_dir or kneaddata_root
    plot_mode = resolve_plot_mode(args.plot_mode)

    logs = list(iter_sample_logs(kneaddata_root))
    if not logs:
        raise SystemExit(f"No kneaddata logs found under {kneaddata_root}")

    metrics = [parse_kneaddata_log(log) for log in logs]
    metrics.sort(key=lambda m: m.sample)

    csv_path = output_dir / args.csv_name
    write_csv(metrics, csv_path)

    print_table(metrics)
    print(f"\nCSV summary written to: {csv_path}")

    plot_path = output_dir / args.plot_name
    if plt is None:
        print("matplotlib not available; skipping plot generation.")
    else:
        result_path = plot_host_contamination(metrics, plot_path, mode=plot_mode)
        if plot_mode == "show":
            print("Stacked bar plot displayed inline.")
        elif plot_mode == "save" and result_path:
            print(f"Stacked bar plot saved to: {result_path}")
        elif plot_mode == "none":
            print("Plot generation skipped.")
        elif result_path is None:
            print("Plot generation produced no figure.")


if __name__ == "__main__":
    main()
