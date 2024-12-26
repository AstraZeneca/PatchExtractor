#!/usr/bin/env python
"""Plot the time scaling of the patch extractor."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from pathlib import Path

from pandas import read_csv

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

    styles = {True: "-or", False: "--k"}

    figure, axis = plt.subplots(1, 1, figsize=(2.5, 2.5))

    for patches in [True, False]:

        frame = time_data.loc[time_data.patches == patches]

        axis.plot(
            frame.workers,
            frame.wall_time_secs,
            styles[patches],
            label=("Full patch extraction" if patches is True else "Masking only"),
        )

    axis.set_xticks(sorted(time_data.workers.unique()))
    axis.set_xlim(left=time_data.workers.min(), right=time_data.workers.max())
    axis.set_xlabel("Workers")

    axis.set_ylim(bottom=0.0, top=40.0)
    axis.set_ylabel("Wall-clock time (seconds)")

    axis.legend()

    figure.tight_layout(pad=0.05)
    figure.savefig("time-scaling.pdf", dpi=250)


if __name__ == "__main__":
    plot_time_scaling(_parse_command_line())
