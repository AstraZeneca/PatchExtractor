#!/usr/bin/env python
"""Profile the ``PatchExtractor``."""

from itertools import product

from time import perf_counter

from typing import List, Union, Dict

from shutil import rmtree

from pathlib import Path

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from argparse import BooleanOptionalAction


from pandas import DataFrame

from patch_extractor import PatchExtractor


def _parse_command_line() -> Namespace:
    """Parse the command-line arguments.

    Returns
    -------
    Namespace
        Command-line arguments.

    """
    parser = ArgumentParser(
        description="Time profile the patch extractor.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "source_path",
        help="Path to the image to profile on.",
        type=Path,
    )

    parser.add_argument(
        "--patch-size",
        type=int,
        help="Length of the square patches to generate.",
        default=512,
    )

    parser.add_argument(
        "--stride",
        type=int,
        help="Stride to use in the sliding-window patch extraction.",
        default=512,
    )

    parser.add_argument(
        "--mpp",
        type=float,
        help="Microns per pixel to use in the patch extraction.",
        default=0.5,
    )

    parser.add_argument(
        "--overview-mpp",
        type=float,
        help="Microns per pixel of the low-power overview image",
        default=4.0,
    )

    parser.add_argument(
        "--min-workers",
        type=int,
        help="Minimum number of workers to profile with.",
        default=1,
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        help="Maximum number of workers to profile with.",
        default=12,
    )

    parser.add_argument(
        "--mask-method",
        type=str,
        help="Method to use when producing the tissue mask (see docs).",
        default="otsu",
    )

    parser.add_argument(
        "--element-size",
        type=float,
        help="Size of the square structuring element (see docs).",
        default=100.0,
    )

    parser.add_argument(
        "--patch-foreground",
        type=float,
        help="Fraction of each patch which must intersect with the tissue mask.",
        default=0.5,
    )

    parser.add_argument(
        "--min_obj_size",
        type=float,
        help="Minimum size of objects allowed in the mask.",
        default=2500.0,
    )

    parser.add_argument(
        "--zip-patches",
        type=bool,
        help="Whether to zip the individual patch directories or not.",
        default=False,
        action=BooleanOptionalAction,
    )

    parser.add_argument(
        "--print-time",
        type=bool,
        help="Whether to print the processing time of each patch.",
        default=True,
        action=BooleanOptionalAction,
    )

    parser.add_argument(
        "--patches",
        type=bool,
        help="Whether to extract patches or just overviews and masks.",
        default=False,
        action=BooleanOptionalAction,
    )

    parser.add_argument(
        "--file-types",
        type=str,
        help="Types of files to allow in the patch extraction.",
        default=[".svs", ".ndpi"],
        nargs="*",
    )

    return parser.parse_args()


def _extract_patches(args: Namespace):
    """Extract patches from target images.

    Parameters
    ----------
    args : Namespace
        Command-line arguments.

    """
    worker_list = range(args.min_workers, args.max_workers + 1)

    save_dir = Path(".tmp-patch-scaling-out-dir")

    profile_data: Dict[str, List[Union[float, int]]] = {
        "workers": [],
        "patches": [],
        "wall_time_secs": [],
    }

    for workers, no_patches in product(worker_list, [True, False]):

        save_dir.mkdir()

        extractor = PatchExtractor(
            patch_size=args.patch_size,
            stride=args.stride,
            mpp=args.mpp,
            overview_mpp=args.overview_mpp,
            workers=workers,
            mask_method=args.mask_method,
            element_size=args.element_size,
            patch_foreground=args.patch_foreground,
            min_obj_size=args.min_obj_size,
            zip_patches=args.zip_patches,
        )

        start_time = perf_counter()

        extractor(
            args.source_path,
            save_dir=save_dir,
            print_time=False,
            no_patches=no_patches,
        )

        stop_time = perf_counter()

        rmtree(save_dir)

        profile_data["workers"].append(workers)
        profile_data["patches"].append(not no_patches)
        profile_data["wall_time_secs"].append(stop_time - start_time)

    profile_frame = DataFrame(profile_data)
    profile_frame.to_csv("profile-data.csv", index=False)


if __name__ == "__main__":
    _extract_patches(_parse_command_line())
