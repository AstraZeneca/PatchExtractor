"""Test the functions in ``misc``."""

from numpy import zeros

from patch_extractor.misc import is_rgb


def test_is_rgb_return_values():
    """Test the values returned by ``is_rgb``."""
    # Test with an rgb image.
    assert is_rgb(zeros((50, 50, 3)))

    # Test with grey image
    assert not is_rgb(zeros((50, 50)))

    # Test with mIF-like dimensions
    assert not is_rgb(zeros((50, 50, 16)))
