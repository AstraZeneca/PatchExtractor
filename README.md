![Maturity level-0](https://img.shields.io/badge/Maturity%20Level-ML--0-red)

# PatchExtractor:
This package serves as a fast and easy WSI patch-extraction tool for computational pathology.

Please see [__the documentation__](https://fluffy-doodle-reqwg84.pages.github.io/).

## Why use this tool?
In computational pathology projects, we invariably have to stop and consider the extraction of patches from WSIs in order to facilitate our analysis. This is often slow, boring and and not what you want to spend your time and energy on.

Using this tool could make your life easier.

## Main advantages

- Multiple masking methods:
  - Different histological stains, staining protocols and WSI scanners give rise to weird and wonderful variability in images which are more or less conducive to certain tissue masking methods.
  - The choice of multiple methods can help with this.

## How to use this tool

The dependencies are defined in the file [pyproject.toml](pyproject.toml).

### Installation

#### Option 1
You can directly install a particular version of the package from GitHub
```bash
https://github.com/AstraZeneca/PatchExtractor/archive/v0.1.0.zip
```
or the default main branch
```bash
https://github.com/AstraZeneca/PatchExtractor/archive/main.zip
```

#### Option 2
Clone the repo and install it locally.

```bash
git clone git@github.com:AstraZeneca/PatchExtractor.git
cd PatchExtractor
pip install .
```
It is advisable to do this inside a Python environment.

#### Option 3
Installing for dev purposes.
```bash
git clone git@github.com:AstraZeneca/PatchExtractor.git
conda env create -f requirements-dev.conda.yaml
conda activate patch-extractor
```


### Using the Python object
One you have built and activated the Python environment:
```python
from patch_extractor import PatchExtractor

extractor = PatchExtractor()

extractor("/path/to/my/wsi-file.svs", "/path/to/desired/save-dir/")

```

### Using the command-line tool
```bash
./extract_patches.py /path/to/source/img-or-dir/ /path/to/save/dir/
```



For full help with the arguments, run
```bash
./extract_patches.py --help
```


## Adding your own masking method

All of the tissue masking methods are in [this file](src/patch_extractor/_mask_utils.py).

To add your own masking method, you need to do two things.

- Add a function to the file ``src/patch_extractor/_mask_utils.py`` of the form
```python
def my_masking_method(overview_img : ndarray) -> ndarray:
  """Produce a tissue mask from ``overview_img``.

  Parameters
  ----------
  overview_img : ndarray
    Low-power RGB overview of the WSI.

  Returns
  -------
  ndarray
      Boolean tissue mask.

  """
  # Your code here ...
```
- Add the masking method to the dictionary ``mask_methods``, which is at the bottom of the file ``src/patch_extractor/_mask_utils.py``. You can (optionally) run ``pytest tests/`` to be sure.

If you wold like your own masking method added to this package, create an issue in the repo, or make a pull request.

## A note on immunofluorescence (IF) images

In IF images, the foreground is lighter than background (the opposite of histology), so choosing masking methods methods which rely on light-dark separation, such as Otsu's method, is not a good idea. KMean, or entropy, are more appropriate.
