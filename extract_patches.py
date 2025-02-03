#!/usr/bin/env python
"""Extract pacthes from a WSI or a directory of WSIs."""

from typing import List

from pathlib import Path

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from argparse import BooleanOptionalAction


from patch_extractor import PatchExtractor


def _parse_command_line() -> Namespace:
    """Parse the command-line argument.

    Returns
    -------
    Namespace
        Command-line arguments.

    """
    parser = ArgumentParser(
        description="Extract patches from a WSI or directory of WSIs.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "source_path",
        help="Path to the image, or directory of images, to extract from.",
        type=Path,
    )

    parser.add_argument(
        "target_path",
        help="Directory to save the patches in.",
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
        "--workers",
        type=int,
        help="Number of workers to use when writing patches to file.",
        default=4,
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
        help="Fraction of each patch which must inersect with the tissue mask.",
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


def _list_target_images(
    source_path: Path,
    file_types: List[str],
) -> List[Path]:
    """List the target images.

    Paramaters
    ----------
    source_path : Path
        Path to the target image or directory.
    file_types : List[str]
        Lists of the file types to include.

    Returns
    -------
    target_wsi : List[Path]
        List of the target WSIs.

    Raises
    ------
    FileNotFoundError
        If no files are found to exist.

    """
    target_wsis: List[Path] = []

    if source_path.is_file():
        target_wsis.append(source_path)
    elif source_path.is_dir():
        target_wsis += list(source_path.glob("*"))
    else:
        msg = f"Target path '{source_path}' has no associated WSIs."
        raise FileNotFoundError(msg)

    target_wsis = list(filter(lambda x: x.suffix in file_types, target_wsis))

    return target_wsis


def _extract_patches(args: Namespace):
    """Extract patches from target images.

    Parameters
    ----------
    args : Namespace
        Command-line arguments.

    """
    source_paths = _list_target_images(args.source_path, args.file_types)

    extractor = PatchExtractor(
        patch_size=args.patch_size,
        stride=args.stride,
        mpp=args.mpp,
        overview_mpp=args.overview_mpp,
        workers=args.workers,
        mask_method=args.mask_method,
        element_size=args.element_size,
        patch_foreground=args.patch_foreground,
        min_obj_size=args.min_obj_size,
        zip_patches=args.zip_patches,
    )

    for source_path in source_paths:

        extractor(
            wsi=source_path,
            save_dir=args.target_path,
            print_time=args.print_time,
            no_patches=not args.patches,
        )


if __name__ == "__main__":
    _extract_patches(_parse_command_line())
