"""Utility functions for creating a tissue mask."""

from typing import Callable, Dict, List

from skimage.util import img_as_ubyte, img_as_float
from skimage.filters import threshold_otsu  # pylint: disable=no-name-in-module
from skimage.color import rgb2gray, rgb2lab  # pylint: disable=no-name-in-module
from skimage.filters.rank import entropy
from skimage.draw import polygon2mask  # pylint: disable=no-name-in-module


from skimage.morphology import binary_dilation, binary_erosion
from skimage.morphology import remove_small_objects

from sklearn.cluster import KMeans  # type: ignore

from numpy import ndarray, ones, floor, log, percentile, bincount, array, zeros


def tissue_mask_from_scratch(
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


def tissue_mask_from_polygons(
    overview_height: int,
    overview_width: int,
    polygons: List[ndarray],
    slide_mpp: float,
    target_mpp: float,
) -> ndarray:
    """Create a tissue mask from a predefined polygon.

    Parameters
    ----------
    overview_height : int
        The total height of the overview image (in pixels).
    overview_width : int
        The total width of the overview image (in pixels).
    polygons : List[ndarray]
        List of arrays of polygon coordinates for the objects in the mask. The
        arrays should have shape (N, 2), and each row should be coords of
        the form (row, col).
    slide_mpp : float
        The microns per pixel of the slide, at level zero.
    target_mpp : float
        The target microns per pixel for the mask image.

    Returns
    -------
    mask : ndarray
        A boolean tissue mask.

    """
    scale_factor = slide_mpp / target_mpp
    mask = zeros((overview_height, overview_width), dtype=bool)

    _check_polygons_conform(polygons)

    for poly in polygons:

        poly = poly.astype(float) * scale_factor

        mask = mask | polygon2mask((overview_height, overview_width), poly)

    return img_as_ubyte(mask)


def _check_polygons_conform(polys: List[ndarray]):
    """Except if the polygons are not of the correct format.

    Parameters
    ----------
    polys : List[ndarray]
        A list of polygons.

    Raises
    ------
    TypeError
        If ``polys`` is not a list.
    TypeError
        If any of the items in ``polys`` is not an ``ndarray``.
    ValueError
        If any of the arrays don't have shape (N, 2)


    """
    if not isinstance(polys, list):
        msg = f"'polygons' should be list, not '{type(polys)}'."
        raise TypeError(msg)

    if not all(map(lambda x: isinstance(x, ndarray), polys)):
        msg = "All items in 'polygons' should be ndarray. Got "
        msg += f"{list(map(type, polys))}"
        raise TypeError(msg)

    if not all(map(lambda x: x.ndim == 2 and x.shape[1] == 2, polys)):
        msg = "'polygons' contents should be 2D arrays of shape (N, 2)."
        raise ValueError(msg)


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


def mask_with_kmeans(overview_img: ndarray) -> ndarray:
    """Create a tissue mask from ``overview_img`` by clustering RGB vecs..

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

    height, width, channels = overview_img.shape

    overview_img = overview_img.reshape(-1, channels)

    k_means = KMeans(n_clusters=2, random_state=123)

    mask = k_means.fit_predict(overview_img).reshape(height, width)

    smallest_cluster = array(bincount(mask.flatten(), minlength=2)).argmin()

    return mask == smallest_cluster


mask_methods: Dict[str, Callable] = {
    "otsu": mask_with_otsu,
    "schreiber": mask_with_schreiber,
    "entropy": mask_with_entropy,
    "od": mask_with_optical_density,
    "luminosity": mask_with_luminosity,
    "kmeans": mask_with_kmeans,
}
