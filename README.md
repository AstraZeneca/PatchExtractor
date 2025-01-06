# PatchExtractor:
A fast and easy WSI patch-extraction tool.

Please see [__the documentation__](https://fluffy-doodle-reqwg84.pages.github.io/).

## Why use this tool?
In computational pathology projects, we invariably have to stop and consider the extraction of patches from WSIs in order to facilitate our analysis. This is often slow, boring and and not what you want to spend your time and energy on.

Using this tool could make your life easier.

## Main advantages

- Multiple masking methods:
  - Different histological stains, staining protocols and WSI scanners give rise to weird and wonderful variability in images which are more or less conducive to certain tissue masking methods.
  - The choice of multiple methods can help with this.

## How to use this tool

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