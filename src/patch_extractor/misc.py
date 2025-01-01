"""Miscellaneous functions."""

from numpy import ndarray, uint8


def is_rgb_uint8(img: ndarray) -> bool:
    """Return ``True`` if ``img`` is RGB and uint8, else ``False``.

    Parameters
    ----------
    img : ndarray
        An image whose RGB uint8 status is to be checked.

    Returns
    -------
    bool
        Whether the image is RGB and uint8.

    """
    return is_rgb(img) and is_uint8(img)


def is_rgb(img: ndarray) -> bool:
    """Return ``True`` if ``img`` is RGB, else ``False``.

    Parameters
    ----------
    img : ndarray
        An image whose RGB status is to be checked.

    Returns
    -------
    bool
        Whether the image is RGB or not.

    """
    return (img.ndim == 3) and (img.shape[-1] == 3)


def is_uint8(img: ndarray) -> bool:
    """Return ``True`` if ``img`` has uint8 dtype, else ``False``.

    Parameters
    ----------
    img : ndarray
        An image whose uint8 status is to be checked.

    Returns
    -------
    bool
        If the image is of dtype uint8.

    """
    return img.dtype == uint8
