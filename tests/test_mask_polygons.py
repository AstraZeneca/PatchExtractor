"""Test the polygons supplied as a mask meet the requirements."""

import pytest

from numpy import array, ndarray, zeros

from patch_extractor._mask_utils import tissue_mask_from_polygons


def test_polygon_return_mask():
    """Test returned mask."""
    # Test with permitted args
    mask = tissue_mask_from_polygons(
        overview_height=15,
        overview_width=15,
        slide_mpp=1.0,
        target_mpp=1.0,
        polygons=[array([(0, 0), (0, 10), (5, 10), (5, 0)])],
    )

    assert isinstance(mask, ndarray)

    assert (mask[:5, :11] == 255).all()
    assert (mask[:, 11:] == 0).all()
    assert (mask[6:, :] == 0).all()


def test_polygon_types():
    """Test the types accepted by the ``polygons``."""
    # Test with permitted args
    _ = tissue_mask_from_polygons(
        overview_height=100,
        overview_width=100,
        slide_mpp=1.0,
        target_mpp=1.0,
        polygons=[array([(0, 0), (0, 10), (10, 10), (10, 0)])],
    )

    # Test with non-list
    with pytest.raises(TypeError):

        # Passing a tuple
        _ = tissue_mask_from_polygons(
            overview_height=100,
            overview_width=100,
            slide_mpp=1.0,
            target_mpp=1.0,
            polygons=(array([(0, 0), (0, 10), (10, 10), (10, 0)])),
        )


def test_polygon_shapes():
    """Test the allowed shapes of the polygons."""
    # Test with permitted args
    _ = tissue_mask_from_polygons(
        overview_height=100,
        overview_width=100,
        slide_mpp=1.0,
        target_mpp=1.0,
        polygons=[array([(0, 0), (0, 10), (10, 10), (10, 0)])],
    )

    # Test wrong number of dims
    with pytest.raises(ValueError):
        _ = tissue_mask_from_polygons(
            overview_height=100,
            overview_width=100,
            slide_mpp=1.0,
            target_mpp=1.0,
            polygons=[zeros((5, 2, 6))],
        )

    # Test wrong shape
    with pytest.raises(ValueError):
        _ = tissue_mask_from_polygons(
            overview_height=100,
            overview_width=100,
            slide_mpp=1.0,
            target_mpp=1.0,
            polygons=[zeros((5, 3))],
        )

    with pytest.raises(ValueError):
        _ = tissue_mask_from_polygons(
            overview_height=100,
            overview_width=100,
            slide_mpp=1.0,
            target_mpp=1.0,
            polygons=[zeros((5, 1))],
        )
