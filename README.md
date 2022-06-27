# This is a fork of the original ONC API
New features and updates are:
- At `onc.getDirectFiles()`:
    - parallelized (threaded) download to speed up the download.
      The number of threads can be set at:
        - the function call `onc.getDirectFiles(..., download_threads=2)` (higher priority)
        - the initialisation of ONC `onc=ONC(..., download_threads: int = 2)`
      
    - takes now `filters_or_results`, which makes it possible to do changes or exclude files of the results from 
  `getListByDevice`, `getListByLocation`, or `getList`.
    - When working with results, the `outPath` can be set per filename.
    - check out the [basic_filter_and_download.py](/examples/basic_filter_and_download.py) example
  
- optimized imports, syntax and code style
- forwarded doc-strings to overloaded function with [`@add_docs`](/onc/util/util.py), e.g., `_OncRealTime.getDirectByLocation` -> `ONC.getDirectByLocation`

## Todo:
- [ ] update test functions for new improvements
- [x] add example for new `onc.getDirectFiles()` features -> [basic_filter_and_download.py](/examples/basic_filter_and_download.py)

## Installation
You can use one of the following two examples to install the fork:
- Recommended for development. Clone the repository and install it with `-e`. Therefore, a `git pull` will be enough to import the updated code.
  Depending on your Python installation adopt python3/pip3 to python/pip, however python3 is required. And run:
```bash
$path_git_repros='/path/to/git_repros'  # adopted the path, be aware that `git clone` creates a directory with the repro name
mkdir $path_git_repros  # create dir
cd $path_git_repros # enter the directory

git clone https://github.com/kholzapfel/api-python-client.git  # downloads the repro
cd api-python-client  # enter the repository directory

python3 -m build  # This will create the files located in the folder `.egg-info`
pip3 install -r requirements.txt  # install the required python packages
pip3 install -U --user -e .  # install the package in developer mode.
```
- Uninstall an existing installation (pip only compares the version number and not the code) and install it from the repository:
```bash
pip uninstall -y onc
pip install -U git+https://github.com/kholzapfel/api-python-client.git@master
```
# Original Readme
## ONC API Python Client Library

This library facilitates access to scientific data hosted by [Ocean Networks Canada](https://oceannetworks.ca) through the
[Oceans 2.0 API](https://wiki.oceannetworks.ca/display/O2A/Oceans+2.0+API+Home) public web services.

This repository updates the [ONC pip package](https://pypi.org/project/onc) which can be installed with the command:

```shell
pip install onc
```

### Documentation

For complete documentation and examples, visit https://wiki.oceannetworks.ca/display/O2A/Oceans+2.0+API+Home


## Maintainers

* Current maintainer: [Dany Cabrera](dcabrera@oceannetworks.ca)
* Current fork-maintainer: [Kilian Holzapfel](kilian.holzapfel@tum.de)
* Previous maintainers: [Allan Rempel](agrempel@uvic.ca), [Ryan Ross](ryanross@uvic.ca)

