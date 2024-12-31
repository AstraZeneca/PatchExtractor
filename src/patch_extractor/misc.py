"""Miscellaneous functions."""

from numpy import ndarray


def is_rgb(img: ndarray) -> bool:
    """Return ``True`` if ``img`` is RGB.

    Parameters
    ----------
    img : ndarray
        An image whose RGB status is to be checked.

    Returns
    -------
    bool

    """
    return (img.ndim == 3) and (img.shape[-1] == 3)
