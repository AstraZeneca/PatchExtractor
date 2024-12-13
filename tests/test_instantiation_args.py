"""Test the arguments of the ``PatchExtractor`` class."""

import pytest

from patch_extractor import PatchExtractor

from patch_extractor._mask_utils import mask_methods


def test_patch_size_arg():
    """Test the patch size argument."""
    # Should work with ints of 2 or more
    _ = PatchExtractor(patch_size=2)
    _ = PatchExtractor(patch_size=3)

    # Should break with non integer
    with pytest.raises(TypeError):
        _ = PatchExtractor(patch_size=1.0)
    with pytest.raises(TypeError):
        _ = PatchExtractor(patch_size=10j)

    # Should break with ints less than 2
    with pytest.raises(ValueError):
        _ = PatchExtractor(patch_size=1)
    with pytest.raises(ValueError):
        _ = PatchExtractor(patch_size=0)
    with pytest.raises(ValueError):
        _ = PatchExtractor(patch_size=-1)


def test_stride_arg():
    """Test the stride argument."""
    # Should work with ints of 1 or more
    _ = PatchExtractor(stride=1)
    _ = PatchExtractor(stride=2)

    # Should break with non integer
    with pytest.raises(TypeError):
        _ = PatchExtractor(stride=1.0)
    with pytest.raises(TypeError):
        _ = PatchExtractor(stride=10j)

    # Should break with ints less than 1
    with pytest.raises(ValueError):
        _ = PatchExtractor(stride=0)
    with pytest.raises(ValueError):
        _ = PatchExtractor(stride=-1)


def test_mpp_arg():
    """Test the mpp argument."""
    # Should work with positive floats
    for mpp in [0.25, 0.5, 1.0]:
        _ = PatchExtractor(mpp=mpp)

    # Should break with non float
    for bad_mpp in [1, 2j, "Not a number"]:
        with pytest.raises(TypeError):
            _ = PatchExtractor(mpp=bad_mpp)

    # Should values of zero or less
    for bad_mpp in [0.0, -1e-4]:
        with pytest.raises(ValueError):
            _ = PatchExtractor(mpp=bad_mpp)


def test_overview_mpp_arg():
    """Test the mpp argument."""
    # Should work with positive floats
    for overview_mpp in [0.25, 0.5, 1.0]:
        _ = PatchExtractor(overview_mpp=overview_mpp)

    # Should break with non float
    for bad_mpp in [1, 2j, "Not a number"]:
        with pytest.raises(TypeError):
            _ = PatchExtractor(overview_mpp=bad_mpp)

    # Should values of zero or less
    for bad_mpp in [0.0, -1e-4]:
        with pytest.raises(ValueError):
            _ = PatchExtractor(overview_mpp=bad_mpp)


def test_workers_arg():
    """Test the workers argument."""
    # Should work with positive ints
    for workers in [1, 2, 3]:
        _ = PatchExtractor(workers=workers)

    # Should break with non int
    for workers in [1.0, 2j]:
        with pytest.raises(TypeError):
            _ = PatchExtractor(workers=workers)

    # Should break with ints less than one
    for workers in [0, -1]:
        with pytest.raises(ValueError):
            _ = PatchExtractor(workers=workers)


def test_mask_method_arg():
    """We need only test the values as they are used to index a dict."""
    # Should work with allowed options
    for method in list(mask_methods.keys()):
        _ = PatchExtractor(mask_method=method)

    # Should break with any other arguments
    for method in ["Sauron the deciever", "Saruman the White"]:

        with pytest.raises(ValueError):
            _ = PatchExtractor(mask_method=method)


def test_element_size_arg():
    """Test the element size argument."""
    # Should work with positive floats
    for size in [0.25, 0.5, 1.0]:
        _ = PatchExtractor(element_size=size)

    # Should break with non float
    for bad_size in [1, 2j, "Not a number"]:
        with pytest.raises(TypeError):
            _ = PatchExtractor(element_size=bad_size)

    # Should values of zero or less
    for bad_size in [0.0, -1e-4]:
        with pytest.raises(ValueError):
            _ = PatchExtractor(element_size=bad_size)


def test_foreground_arg():
    """Test the foreground argument."""
    # Should work with floats on [0.0, 1.0]
    for foreground in [0.0, 0.5, 1.0]:
        _ = PatchExtractor(patch_foreground=foreground)

    # Should break with non-float
    for bad_arg in [1, 0.5j]:
        with pytest.raises(TypeError):
            _ = PatchExtractor(patch_foreground=bad_arg)

    # Should break with floats not on [0.0, 1.0]
    for bad_arg in [-0.0001, 1.0001]:
        with pytest.raises(ValueError):
            _ = PatchExtractor(patch_foreground=bad_arg)


def test_min_obj_size_arg():
    """Test the minimum object size argument."""
    # Should work with float of zero or more.
    for obj_size in [0.0, 10.0, 2500.0]:
        _ = PatchExtractor(min_obj_size=obj_size)

    # Should break with non float
    for obj_size in [1, 10j]:
        with pytest.raises(TypeError):
            _ = PatchExtractor(min_obj_size=obj_size)

    # Should break with floats less than zero
    for obj_size in [-0.0001, -100.0]:
        with pytest.raises(ValueError):
            _ = PatchExtractor(min_obj_size=obj_size)


def test_zip_patches_arg():
    """Test the ``zip_patches`` argument."""
    # Should work with bool.
    for zip_patches in [True, False]:
        _ = PatchExtractor(zip_patches=zip_patches)

    # Should break with any other argument type.
    for zip_patches in [0.0, 1.0, 5j, "Batman"]:

        with pytest.raises(TypeError):
            _ = PatchExtractor(zip_patches=zip_patches)
