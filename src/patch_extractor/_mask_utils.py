"""Utility functions for creating a tissue mask."""

from typing import Callable, Dict

from skimage.util import img_as_ubyte, img_as_float
from skimage.filters import threshold_otsu  # pylint: disable=no-name-in-module
from skimage.color import rgb2gray, rgb2lab  # pylint: disable=no-name-in-module
from skimage.filters.rank import entropy


from skimage.morphology import binary_dilation, binary_erosion
from skimage.morphology import remove_small_objects

from numpy import ndarray, ones, floor, log, percentile


def create_tissue_mask(
    overview_image: ndarray,
    method: str,
    overview_mpp: float,
    element_size: float,
    min_obj_size: float,
) -> ndarray:
    """Create a tissue mask.

    Parameters
    ----------
    overview_img : ndarray
        RGB overview of a WSI.
    method : str
        Method to create the mask with.]
    overview_mpp : float
        The microns per pixel of the overview image.
    element_size : float
        The length of the structuring element, in microns.
    min_obj_size : float
        The minimum object size, in microns, allowed in the mask.

    """
    size = int(floor(element_size / overview_mpp))

    if method != "entropy":
        mask_img = mask_methods[method](overview_image)
    else:
        mask_img = mask_methods[method](overview_image, ones((size, size)))

    mask_img = binary_dilation(mask_img, footprint=ones((size, size)))

    mask_img = binary_erosion(mask_img, footprint=ones((size, size)))

    pixel_area = overview_mpp * overview_mpp

    mask_img = remove_small_objects(mask_img, min_obj_size / pixel_area)

    return img_as_ubyte(mask_img)


def mask_with_otsu(overview_img: ndarray) -> ndarray:
    """Create a tissue mask from``overview_img``.

    Parameters
    ----------
    overview_img : ndarray
        RGB overview image.

    Returns
    -------
    ndarray
        The binary mask image.

    """
    overview_img = rgb2gray(overview_img)

    return overview_img < threshold_otsu(overview_img)


def mask_with_schreiber(overview_img: ndarray) -> ndarray:
    """Create a tissue mask from ``overview_img``.

    Parameters
    ----------
    overview_img : ndarray
        The RGB overview image on a WSI.

    Returns
    -------
    ndarray
        A binary tissue mask.

    """
    overview_img = img_as_float(overview_img)

    red = overview_img[:, :, 0]
    green = overview_img[:, :, 1]
    blue = overview_img[:, :, 2]

    representation = (red - green).clip(0.0) * (blue - green).clip(0.0)

    return representation > threshold_otsu(representation)


def mask_with_optical_density(overview_img: ndarray):
    """Create a tissue mask using the optical density of ``overview_img``.

    Parameters
    ----------
    overview_img : ndarray
        A low power, RGB overview of the WSI.

    Returns
    -------
    ndarray
        A binary tissue mask.

    """
    overview_img = img_as_float(overview_img).clip(1.0 / 255.0, 1.0)

    absorbance = -log(overview_img).sum(axis=2)

    absorbance = absorbance.clip(*percentile(absorbance, (1, 99)))

    return absorbance > threshold_otsu(absorbance)


def mask_with_entropy(overview_img: ndarray, footprint: ndarray) -> ndarray:
    """Create a tissue mask from ``overview_img``.

    Parameters
    ----------
    overview_img : ndarray
        The RGB overview image on a WSI.
    footprint : ndarray
        The footprint to use in the entropy filter.

    Returns
    -------
    ndarray
        A binary tissue mask.

    """
    entropy_img = entropy(
        img_as_ubyte(rgb2gray(overview_img)),
        footprint=footprint,
    )

    return entropy_img > threshold_otsu(entropy_img)


def mask_with_luminosity(overview_img: ndarray) -> ndarray:
    """Create a tissue mask from ``overview_img`` using its luminosity.

    Parameters
    ----------
    overview_img : ndarray
        The RGB overview image on a WSI.

    Returns
    -------
    ndarray
        A binary tissue mask.

    """
    overview_img = img_as_float(overview_img)

    lum = rgb2lab(overview_img)[:, :, 0]

    return lum < threshold_otsu(lum)


mask_methods: Dict[str, Callable] = {
    "otsu": mask_with_otsu,
    "schreiber": mask_with_schreiber,
    "entropy": mask_with_entropy,
    "optical-density": mask_with_optical_density,
    "luminosity": mask_with_luminosity,
}
