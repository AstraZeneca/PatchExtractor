#!/usr/bin/env python
"""Plot the time scaling of the patch extractor."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from pathlib import Path

from pandas import read_csv

from numpy import array

import matplotlib.pyplot as plt


def _parse_command_line() -> Namespace:
    """Parse the command-line arguments.

    Returns
    -------
    Namespace
        The command-line arguments.

    """
    parser = ArgumentParser(
        description="Plot the patch extractor time scaling.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "profile_csv",
        type=Path,
        help="Path to the time scaling csv file.",
    )

    return parser.parse_args()


def plot_time_scaling(args: Namespace):
    """Plot the time scaling of of the patch extractor.

    Parameters
    ----------
    args : Namespace
        Command-line arguments.

    """
    time_data = read_csv(args.profile_csv)

    styles = {True: "-o", False: "--"}

    figure, axis = plt.subplots(1, 1, figsize=(4, 2))

    for patches in [True, False]:

        frame = time_data.loc[time_data.patches == patches]

        means = frame.groupby("workers").wall_time_secs.mean().reset_index()

        print("With patches" if patches is True else "Without patches")
        print(means)
        print("\n")

        axis.plot(
            means.workers,
            means.wall_time_secs,
            styles[patches],
            label=("Full patch extraction" if patches is True else "Masking only"),
            color=array([122, 1, 119]) / 255.0 if patches is True else "k",
        )

    axis.set_xticks(sorted(time_data.workers.unique()))
    axis.set_xlim(left=time_data.workers.min(), right=time_data.workers.max())
    axis.set_xlabel("Workers")

    axis.set_ylim(bottom=0.0, top=40.0)
    axis.set_ylabel("Wall-clock time (seconds)")

    x_min, x_max = axis.get_xlim()
    y_min, y_max = axis.get_ylim()

    axis.set_aspect(0.5 * (x_max - x_min) / (y_max - y_min))

    axis.legend()

    figure.tight_layout(pad=0.05)
    figure.savefig("time-scaling.pdf", dpi=250)


if __name__ == "__main__":
    plot_time_scaling(_parse_command_line())
