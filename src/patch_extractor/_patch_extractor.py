"""WSI patch-extraction tool."""

from time import perf_counter


from typing import Union

from pathlib import Path

from skimage.io import imsave, imread

from . import _argument_processing as ap
from . import _region_extraction as reg_ext
from ._mask_utils import create_tissue_mask
from ._patch_utils import create_patch_coord_df, mask_intersection, extract_patches

from ._mpp_utils import requested_mpp_less_than_slide


class PatchExtractor:  # pylint: disable=too-many-instance-attributes
    """WSI patch-extraction tool.

    Parameters
    ----------
    patch_size : int, optional
        Size of the patches to extract.
    stride : int, optional
        Stride to the sliding window used to extract patches.
    mpp : float, optional
        The number of microns per pixel in the extracted patches.
    overview_mpp : float, optional
        The microns per pixel of the low-power overiew image.
    workers : int, optional
        The number of workers to use, in parallel, when extracting patches
        (has not affect on overview image or masking steps).
    mask_method : str, optional
        Method to use when create the tissue mask.
    element_size : float, optional
        The length of the square dilation, erosion and entropy element to use
        in masking (in microns).
    area_threshold : float, optional
        The size, beneath which, objects are removed from the mask.
    patch_foreground : float, optional
        The fraction of a patch which must contain foreground for it to be
        considered. Should be on [0.0, 1.0].
    workers : int, optional
        The number of workers to use in the patch extraction.
    min_obj_size : float, optional
        The area of the smallest objects, in square microns, permitted in the
        mask.
    zip_patches : bool, optional
        If ``True``, the patch subdirectory the patches are writtent to will
        instead be a zipfile.

    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        patch_size: int = 512,
        stride: int = 256,
        mpp: float = 0.5,
        overview_mpp: float = 4.0,
        workers: int = 8,
        mask_method: str = "otsu",
        element_size: float = 100.0,
        area_threshold: float = 0.0,
        patch_foreground: float = 0.5,
        min_obj_size: float = 2500.0,
        zip_patches: bool = False,
    ):
        """Set up ``PatchExtractor``."""
        self._patch_size = ap.process_patch_size_arg(patch_size)
        self._stride = ap.process_stride_arg(stride)
        self._patch_mpp = ap.process_mpp_arg(mpp)
        self._overview_mpp = ap.process_mpp_arg(overview_mpp)
        self._workers = ap.process_num_workers_arg(workers)
        self._mask_method = ap.process_mask_method_arg(mask_method)
        self._element_size = ap.process_element_size(element_size)
        self._area_threshold = ap.process_area_threshold(area_threshold)
        self._foreground = ap.process_foreground_arg(patch_foreground)
        self._min_obj_size = ap.process_min_object_size_arg(min_obj_size)
        self._zip_patches = ap.process_zip_patches_arg(zip_patches)

    _slide_path = Path("")
    _save_dir = Path("")

    def _overview_file_path(self, img_name: str) -> Path:
        """Create the path at which the overview image should be saved.

        Parameters
        ----------
        img_name : str
            The name of the image: 'overview', 'masked-image', 'tissue-mask'.

        Returns
        -------
        overview_path : Path
            File path of the overview image.

        """
        overview_path = self._save_dir / self._slide_path.name
        overview_path /= f"{img_name}-{self._overview_mpp:.3f}-mpp.png"

        return overview_path

    def _create_overview_image(self):
        """Create a low-power overview image of the slide."""
        requested_mpp_less_than_slide(self._slide_path, self._overview_mpp)

        overview = reg_ext.extract_overview_image(
            self._slide_path,
            self._overview_mpp,
        )

        overview_path = self._overview_file_path("overview")
        overview_path.parent.mkdir(parents=True, exist_ok=True)

        imsave(overview_path, overview)

    def _create_mask_images(self):
        """Create an image of the tissue mask."""
        overview_image = imread(self._overview_file_path("overview"))

        mask = create_tissue_mask(
            overview_image,
            self._mask_method,
            self._overview_mpp,
            self._element_size,
            self._min_obj_size,
        )

        imsave(self._overview_file_path("tissue-mask"), mask)

        overview_image[~mask.astype(bool)] = 0
        imsave(self._overview_file_path("masked-image"), overview_image)

    def _extract_patches(self):
        """Extract patches from a WSI."""
        requested_mpp_less_than_slide(self._slide_path, self._overview_mpp)

        coords = create_patch_coord_df(
            self._slide_path,
            self._patch_size,
            self._stride,
            self._patch_mpp,
        )

        mask_intersection(
            coords,
            self._slide_path,
            self._overview_file_path("tissue-mask"),
            self._overview_mpp,
        )

        coords = coords.loc[coords.mask_frac >= self._foreground]

        save_dir = self._save_dir / f"{self._slide_path}/patches"
        save_dir /= f"L={self._patch_size},mpp={self._patch_mpp:.3f}"

        extract_patches(
            coords,
            self._slide_path,
            self._patch_size,
            save_dir,
            self._workers,
            self._zip_patches,
        )

    def __repr__(self):
        """Return a pretty string for printing the class.

        Returns
        -------
        pretty : str
            A pretty string representing the class.

        """
        pretty = "\nPatchExtractor\n"
        pretty += "--------------\n"
        pretty += f"patch_size:\t {self._patch_size}\n"
        pretty += f"stride:\t\t {self._stride}\n"
        pretty += f"mpp:\t\t {self._patch_mpp:.4f}\n"
        return pretty

    def __call__(
        self,
        wsi: Union[str, Path],
        save_dir: Union[str, Path],
        print_time: bool = True,
        no_patches: bool = False,
    ):
        """Extract patches from ``wsi``.

        Parameters
        ----------
        wsi : Path
            Path to the whole-slide image.
        save_dir : Path
            The parent directory to write in.
        print_time : bool, optional
            Whether to print the processing time for ``wsi`` or not.
        no_patches : bool
            If ``True``, we create the overview image and tissue mask, only.

        """
        start = perf_counter()

        self._slide_path = Path(wsi)
        self._save_dir = Path(save_dir)

        self._create_overview_image()
        self._create_mask_images()

        if no_patches is False:
            self._extract_patches()

        stop = perf_counter()

        if print_time:
            print(f"Processed '{wsi}' in {stop - start:.6f} seconds.")
