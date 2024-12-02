"""Utility functions for patch-level coordinates."""

from typing import Dict, Any

from multiprocessing import Pool

from pathlib import Path

from itertools import product

from tiffslide import TiffSlide

from skimage.io import imread, imsave
from skimage.util import img_as_ubyte
from skimage.transform import resize  # pylint: disable=no-name-in-module

from pandas import DataFrame

from ._mpp_utils import get_slide_mpp


def create_patch_coord_df(
    slide_path: Path,
    patch_size: int,
    stride: int,
    target_mpp: float,
) -> DataFrame:
    """Create a ``DataFrame`` holding the patch coordinates.

    Parameters
    ----------
    slide_path : Path
        Path to the WSI.
    patch_size : int
        Length of the square patches.
    stride : int
        The stride to use when creating the patches.
    scale : float
        Scale factor to apply to the coordinates.

    Returns
    -------
    DataFrame
        The patch-level coords. The column titles are 'left', 'right', 'top'
        and 'bottom'.

    """
    with TiffSlide(slide_path) as slide:
        width, height = slide.dimensions

    scale = target_mpp / get_slide_mpp(slide_path)
    patch_size = round(patch_size * scale)
    stride = round(stride * scale)

    coords = DataFrame(
        columns=["left", "top"],
        data=product(range(0, width, stride), range(0, height, stride)),
    )
    coords["right"] = coords["left"] + patch_size
    coords["bottom"] = coords["top"] + patch_size

    return coords


def mask_intersection(
    coords: DataFrame,
    slide_path: Path,
    mask_path: Path,
    overview_mpp: float,
):
    """Added the patch-mask intersection to ``coords``.

    Parameters
    ----------
    coords : DataFrame
        Coordinate data frame.
    slide_path : Path
        Path to the WSI.
    mask_path : Path
        Path to the mask image.
    overview_mpp : float
        The microns per pixel of the overview image.

    """
    scale = get_slide_mpp(slide_path) / overview_mpp

    mask = imread(mask_path).astype(bool)

    rescaled = (coords * scale).round(0).convert_dtypes()

    coords["mask_frac"] = rescaled.apply(
        lambda x: mask[x.top : x.bottom, x.left : x.right].mean(), axis=1
    )


def _extract_patch(
    slide_path: Path,
    left: int,
    right: int,
    top: int,
    bottom: int,
):
    """Extract patch from the WSI.

    Parameters
    ----------
    slide_path : Path
        Path to the WSI.
    left : int
        Left patch coord.


    """
    with TiffSlide(slide_path) as slide:
        region = slide.read_region(
            location=(left, top),
            level=0,
            size=(right - left, bottom - top),
            as_array=True,
        )
    return region


def _save_patch(info: Dict[str, Any]):
    """Save the patch to file."""
    patch = _extract_patch(
        slide_path=info["slide_path"],
        left=info["left"],
        right=info["right"],
        top=info["top"],
        bottom=info["bottom"],
    )

    patch = resize(
        image=patch,
        output_shape=(info["patch_size"], info["patch_size"]),
    )

    file_name = info["save_dir"]
    file_name /= f"{info['slide_path'].name}---[x={info['left']},y={info['top']}].png"

    file_name.parent.mkdir(parents=True, exist_ok=True)

    imsave(file_name, img_as_ubyte(patch))


def extract_patches(
    coords: DataFrame,
    slide_path: Path,
    patch_size: int,
    save_dir: Path,
    workers: int,
):
    """Extract patches from the WSI.

    Parameters
    ----------
    coords : DataFrame
        Patch coords in the level-zero reference frame.
    slide_path : Path
        Path to the WSI.
    patch_size : int
        Size of the patches to save to file.
    save_dir : Path
        Directory to save the patches in.
    workers : int
        The number of workers to use in the patch extraction.

    """
    coords = coords.copy()
    coords["slide_path"] = slide_path
    coords["save_dir"] = save_dir
    coords["patch_size"] = patch_size

    keys = [
        "left",
        "right",
        "top",
        "bottom",
        "slide_path",
        "save_dir",
        "patch_size",
    ]

    patch_info = coords[keys].apply(dict, axis=1)

    with Pool(processes=workers) as pool:
        pool.map(_save_patch, patch_info)
