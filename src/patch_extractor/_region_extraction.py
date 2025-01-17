"""Utility functions for extracting regions of interest."""

from pathlib import Path

from numpy import ndarray

from skimage.util import img_as_ubyte
from skimage.transform import rescale  # pylint: disable=no-name-in-module

from tiffslide import TiffSlide

from patch_extractor import _mpp_utils as mu
from patch_extractor.misc import is_rgb_uint8


def extract_overview_image(wsi: Path, overview_mpp: float) -> ndarray:
    """Extract the full level as a numpy array.

    Parameters
    ----------
    wsi : Path
        Path to the WSI.
    overview_mpp : float
        The microns per pixel of the overview image.

    Returns
    -------
    ndarray
        The full level as an RGB image, resized to have ``overview_mpp``.

    """
    level = mu.get_nearest_level(wsi, overview_mpp)
    scale_factor = mu.get_scale_factor(wsi, overview_mpp) ** -1.0

    with TiffSlide(wsi) as slide:

        dims = slide.level_dimensions[level]
        region = slide.read_region(
            location=(0, 0),
            level=level,
            size=dims,
            as_array=True,
        )

    if not is_rgb_uint8(region):
        region = region.mean(axis=2)[:, :, None].repeat(3, axis=2)
        region /= region.max()  # type: ignore

    return img_as_ubyte(rescale(region, scale_factor, channel_axis=2))
