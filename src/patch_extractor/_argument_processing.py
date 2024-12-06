"""Function to process the arguments of the ``PatchExtractor``."""

from . import _mask_utils as mu


def process_patch_size_arg(patch_size: int) -> int:
    """Process the patch size argument.

    Parameters
    ----------
    patch_size : int
        The size of the patches to extract.

    Returns
    -------
    patch_size : int
        See Parameters.

    Raises
    ------
    TypeError
        If ``patch_size`` is not an in.
    ValueError
        If ``patch_size`` is less than 2.

    """
    if not isinstance(patch_size, int):
        raise TypeError(f"Patch size should be int, got {type(patch_size)}.")

    if patch_size < 2:
        raise ValueError(f"Patch size should be >= 2, got '{patch_size}'.")

    return patch_size


def process_stride_arg(stride: int) -> int:
    """Process the stride argument.

    Parameters
    ----------
    stride : int
        The stride to use in the patch extraction.

    Returns
    -------
    stride : int
        See Parameters.

    Raises
    ------
    TypeError
        If ``stride`` is not an int.
    ValueError
        If stride is less than one.

    """
    if not isinstance(stride, int):
        raise TypeError(f"Stride should be int, got {type(stride)}.")

    if stride < 1:
        raise ValueError(f"Stride should be >= 1, got '{stride}'.")

    return stride


def process_mpp_arg(mpp: float) -> float:
    """Process the microns per pixel argument.

    Parameters
    ----------
    mpp : float
        The microns per pixel

    Returns
    -------
    mpp : float
        See Parameters.

    Raises
    ------
    TypeError
        If ``mpp`` is not a float.

    """
    if not isinstance(mpp, float):
        msg = f"Microns per pixel should be float, got '{type(mpp)}'."
        raise TypeError(msg)

    if mpp <= 0.0:
        raise ValueError(f"Microns per pixel should be positive, got '{mpp}'.")

    return mpp


def process_num_workers_arg(num_workers: int) -> int:
    """Process the number of workers argument.

    Parameters
    ----------
    num_workers : int
        Number of workers to use in the patch extraction.

    Returns
    -------
    See Parameters.

    Raises
    ------
    TypeError
        If ``num_workers`` is not an int.
    ValueError
        If ``num_workers`` is not at least one.

    """
    if not isinstance(num_workers, int):
        msg = f"'num_workers' should be int, got {type(num_workers)}."
        raise TypeError(msg)

    if num_workers < 1:
        msg = f"'num_workers' should be at least one, got {num_workers}."
        raise ValueError(msg)

    return num_workers


def process_mask_method_arg(mask_method: str):
    """Process the mask method argument.

    Parameters
    ----------
    mask_method : str
        The method to use when masking the tissue.

    Returns
    -------
    mask_method : str
        A lower-case version of the input argument.
    ValueError
        If ``mpp`` is not greater than zero.

    """
    mask_method = mask_method.lower()

    # pylint: disable=consider-iterating-dictionary
    if not mask_method.lower() in mu.mask_methods.keys():
        msg = f"Unrecognised mask option '{mask_method}'. Please choose from "
        msg += f"'{list(mu.mask_methods.keys())}'."
        raise ValueError(msg)

    return mask_method


def process_element_size(element_size: float) -> float:
    """Process the element size argument.

    Parameters
    ----------
    element_size : float
        The length of the element for dilation, erosion and entropy.

    Returns
    -------
    element_size : float
        See Parameters.

    Raises
    ------
    TypeError
        If ``element_size`` is not a float.
    ValueError
        If ``element_size`` is not greater than zero.

    """
    if not isinstance(element_size, float):
        msg = f"Element size should be float, got '{type(element_size)}'."
        raise TypeError(msg)

    if element_size <= 0.0:
        raise ValueError(f"Element size should be > 0, got '{element_size}'.")

    return element_size


def process_area_threshold(area_threshold: float) -> float:
    """Process the ``area_threshold`` argument.

    Parameters
    ----------
    area_threshold : float
        The area beneath which objects are removed from the mask.

    Returns
    -------
    area_threshold : float
        The area beneath which objects are removed from the mask.


    Raises
    ------
    TypeError
        If ``area_threshold`` is not a float.
    ValueError
        If ``area_threshold`` is less than zero

    """
    if not isinstance(area_threshold, float):
        msg = f"Area threshold should be float, got '{type(area_threshold)}'."
        raise TypeError(msg)

    if area_threshold < 0.0:
        msg = f"Area threshold should be >= 0, got '{area_threshold}'."
        raise ValueError(msg)

    return area_threshold


def process_foreground_arg(foreground: float) -> float:
    """Process the ``foreground`` argument.

    Parameters
    ----------
    foreground : float
        The fraction of foreground that should be in a patch.

    Returns
    -------
    foreground : float
        See parameters.

    Raises
    ------
    TypeError
        If ``foreground`` is not a float.
    ValueError
        If ``foreground`` is not on [0.0, 1.0].

    """
    if not isinstance(foreground, float):
        msg = f"'foreground' should be float, got {type(foreground)}."
        raise TypeError(msg)

    if not 0.0 <= foreground <= 1.0:
        msg = f"'foreground' should be on [0, 1], got '{foreground}'."
        raise ValueError(msg)

    return foreground


def process_min_object_size_arg(min_obj_size: float) -> float:
    """Process the ``min_obj_size`` argument.

    Parametersmin_obj_size
    ----------
    min_obj_size : float
        The area, in microns, of the smallest object allowed in the mask.

    Returns
    -------
    foreground : float
        See parameters.

    Raises
    ------
    TypeError
        If ``min_obj_size`` is not a float.
    ValueError
        If ``min_obj_size`` is not zero or more

    """
    if not isinstance(min_obj_size, float):
        msg = f"'min_obj_size' should be float, got {type(min_obj_size)}."
        raise TypeError(msg)

    if min_obj_size < 0.0:
        msg = f"'min_obj_size' should be > 0.0, got '{min_obj_size}'."
        raise ValueError(msg)

    return min_obj_size


def process_zip_patches_arg(zip_patches: bool) -> bool:
    """Type check the ``zip_patches`` argument.

    Parameters
    ----------
    zip_patches : bool
        Boolean arg determing whether the patches are saved in a zip.

    Raises
    ------
    TypeError
        If ``zip_patches`` is not a bool.

    """
    if not isinstance(zip_patches, bool):
        msg = f"'zip_patches' should be bool, got '{type(zip_patches)}'."
        raise TypeError(msg)

    return zip_patches
