"""Functions for managing pixel-level scale calculations."""

from pathlib import Path

from tiffslide import TiffSlide

from numpy import ndarray, array


def get_slide_mpp(wsi: Path) -> float:
    """Get the microns per pixel of the slide.

    Parameters
    ----------
    wsi : Path
        Path to the WSI.

    Returns
    -------
    mpp : float
        The microns per pixel of the slide.

    """
    with TiffSlide(wsi) as slide:

        if "tiffslide.mpp-x" in slide.properties:
            return float(slide.properties["tiffslide.mpp-x"])

        if "tiffslide.mpp-y" in slide.properties:
            return float(slide.properties["tiffslide.mpp-y"])

    msg = f"Unable to determine microns per pixel from slide '{wsi}'"
    raise RuntimeError(msg)


def get_level_mpps(wsi: Path) -> ndarray:
    """Get the microns per pixel at each level.

    Parameters
    ----------
    wsi : Path
        Path to the WSI.

    Returns
    -------
    levels_mpp : ndarray
        Microns per pixel at each level.

    """
    with TiffSlide(wsi) as slide:

        level_downsamples = array(slide.level_downsamples)

    return get_slide_mpp(wsi) * level_downsamples


def get_nearest_level(wsi: Path, target_mpp: float) -> int:
    """Get the nearest level to the target magnification.

    Parameters
    ----------
    wsi : Path
        Path to the whole-slide image.
    target_mpp : float
        The desired microns per pixel of an output image.

    """
    return int(abs(get_level_mpps(wsi) - target_mpp).argmin())


def get_scale_factor(wsi: Path, target_mpp: float) -> float:
    """Get the scale factor between ``target_mpp`` and ``level``.

    Parameters
    ----------
    wsi : Path
        Path to the whole-slide image.
    target_mpp : float
        The desired microns per pixel.
    level : int
        The level in the tif we sampling from.

    Returns
    -------
    scale : float
        The target microns per pixel divided the level microns per pixel.

    """
    return target_mpp / get_level_mpps(wsi)[get_nearest_level(wsi, target_mpp)]


def requested_mpp_less_than_slide(wsi: Path, requested_mpp: float):
    """Check the requested mpp is not less than the slide's.

    Parameters
    ----------
    wsi : Path
        Path to the whole-slide image.
    requested_mpp : float
        Requested mpp from the user.

    Raises
    ------
    ValueError
    if ``requested_mpp`` is less than ``wsi``'s.

    """
    slide_mpp = get_slide_mpp(wsi)

    if requested_mpp < slide_mpp:
        msg = f"Requested mpp '{requested_mpp}' is less than slide {wsi}'s "
        msg += f"{slide_mpp}"
        raise ValueError(msg)
