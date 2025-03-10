"""WSI patch-extraction tool."""

from time import perf_counter


from typing import Union, Optional, List

from pathlib import Path

from skimage.io import imsave, imread

from numpy import ndarray

from pandas import read_csv

from . import _argument_processing as ap
from . import _region_extraction as reg_ext
from ._mask_utils import (
    tissue_mask_from_scratch,
    tissue_mask_from_polygons,
)
from ._patch_utils import create_patch_coord_df, mask_intersection, extract_patches

from ._mpp_utils import requested_mpp_less_than_slide, get_slide_mpp


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
        The microns per pixel of the low-power overview image.
    workers : int, optional
        The number of workers to use, in parallel, when extracting patches
        (has not affect on overview image or masking steps).
    mask_method : str, optional
        Method to use when create the tissue mask:

          - ``"otsu"`` for Otsu's method.
          - ``"schreiber"`` for Schreiber's method.
          - ``"entropy"`` to use the entropy method.
          - ``"od"`` for the optical density method.
          - ``"luminosity"`` for the luminosity method.
          - ``"kmeans"`` to use KMeans clustering on the RGB vectors.

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

        imsave(overview_path, overview, check_contrast=False)

    def _create_mask_images(self, mask_polys: Optional[List[ndarray]] = None):
        """Create an image of the tissue mask.

        Parameters
        ----------
        mask_poly : List[ndarray], optional
            A list of arrays of (row, col) coordinates of the points on the
            polygons in the tissue mask. There should be one polygon per
            object, and the arrays should have shape (N, 2).

        """
        overview_image = imread(self._overview_file_path("overview"))

        if mask_polys is None:

            mask = tissue_mask_from_scratch(
                overview_image,
                self._mask_method,
                self._overview_mpp,
                self._element_size,
                self._min_obj_size,
            )
        else:

            mask = tissue_mask_from_polygons(
                overview_height=overview_image.shape[0],
                overview_width=overview_image.shape[1],
                polygons=mask_polys,
                slide_mpp=get_slide_mpp(self._slide_path),
                target_mpp=self._overview_mpp,
            )

        imsave(
            self._overview_file_path("tissue-mask"),
            mask,
            check_contrast=False,
        )

        overview_image[~mask.astype(bool)] = 0
        imsave(
            self._overview_file_path("masked-image"),
            overview_image,
            check_contrast=False,
        )

    def _extract_patches(self, patch_csv: Optional[Path] = None):
        """Extract patches from a WSI.

        Parameters
        ----------
        patch_csv : Path, optional
            Path to a csv file of predetermined patches (see docstring of
            ``__call__`` method).

        """
        requested_mpp_less_than_slide(self._slide_path, self._overview_mpp)

        if patch_csv is None:
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
        else:
            coords = read_csv(patch_csv)

        save_dir = self._save_dir / f"{self._slide_path.name}/patches"
        save_dir /= f"L={self._patch_size}-mpp={self._patch_mpp:.3f}"

        csv = Path(str(save_dir).replace("/patches/", "/manifests/") + ".csv")
        csv.parent.mkdir(parents=True)
        coords.to_csv(csv, index=False)

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
        patch_csv: Optional[Path] = None,
        mask_polygons: Optional[List[ndarray]] = None,
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
        patch_csv : Path, optional
            Path to a csv file containing pre-determined patch coords in the
            level zero reference frame. Must contain columns "left", "right",
            "top", "bottom". This is useful if want to extract paired patches
            from a histological WSI and a WSI segmentation mask. If specified,
            aside from the patch size, the patch parameters specified when
            this class was instantiated are ignored, and no tissue mask is
            generated.
        mask_polygons : List[ndarray], optional
            Polygons delineating each of the objects in the tissue mask. There
            should be one array per object, each of shape (N, 2), with coords
            of the form (row, col). The coordinates should be in the
            level-zero reference frame of the WSI. If ``patch_csv`` is
            supplied, this argument is ignored.

            ```
            mask_polygon=[np.array([(row, col), ...]), np.array([(row, col), ...])]
            ```

        """
        start = perf_counter()

        self._slide_path = Path(wsi)
        self._save_dir = Path(save_dir)

        self._create_overview_image()

        if patch_csv is None:
            self._create_mask_images(mask_polys=mask_polygons)

        if no_patches is False:
            self._extract_patches(patch_csv=patch_csv)

        stop = perf_counter()

        if print_time:
            print(f"Processed '{wsi}' in {stop - start:.6f} seconds.")
