"""Test the functions in ``misc``."""

from numpy import zeros, uint8

from patch_extractor.misc import is_rgb, is_uint8, is_rgb_uint8


def test_is_rgb_return_values():
    """Test the values returned by ``is_rgb``."""
    # Test with an rgb image.
    assert is_rgb(zeros((50, 50, 3)))

    # Test with grey image
    assert not is_rgb(zeros((50, 50)))

    # Test with mIF-like dimensions
    assert not is_rgb(zeros((50, 50, 16)))


def test_is_uint8_return_values():
    """Test the values returned by ``is_uint8``."""
    # Test with a uint8 array
    assert is_uint8(zeros(10, dtype=uint8))

    # Test with non uint8 types
    for not_uint in [int, float, complex]:
        assert not is_uint8(zeros(10, dtype=not_uint))


def test_is_rgb_uint8_return_values():
    """Test the values returned by ``is_rgb``."""
    # Test with an RGB image of uint8
    assert is_rgb(zeros((50, 50, 3), dtype=uint8))

    # Test with RGB shape but the wrong type
    for wrong_type in [int, float, complex, bool, str]:
        assert not is_rgb_uint8(zeros((50, 50, 3), dtype=wrong_type))

    # Test with the correct type but bad shape
    for shape in [(10,), (50, 50), (50, 50, 1), (50, 50, 8)]:
        assert not is_rgb_uint8(zeros(shape, dtype=uint8))
