# This is a fork of the original ONC API
New features and updates are:
- `onc.getDirectFiles()`:
    - parallelized (threaded) download within `onc.getDirectFiles(..., download_threads=2)`. The number of threads can be 
  either set at the function call oor the initialisation (higher priority), or
  `ONC(..., download_threads: int = 2)` defines the number of threads.
    - takes now `filters_or_results`, which makes it possible to do changes or exclude files of the results from 
  `getListByDevice`, `getListByLocation`, or `getList`.
    - When working with results, the `outPath` can be set per filename. 
- optimized imports, syntax and code style
- forwarded Docstrings to overloaded function (`_OncRealTime.getDirectByLocation` -> `ONC.getDirectByLocation`)

## Todo:
- [ ] update test functions for new improvements
- [ ] add example for new `onc.getDirectFiles()` features

## Installation
You can use one of the following two examples to install the fork:
- clone the repository and:
  ```bash
  pip install -e dir/to/repro
  ```
  Recommended for development. Make sure to install the requirements, as i.e. a `git pull` will be enough to import the updated code.
- Uninstall an existing installation (pip only compares the version number and not the code) and install it from the repository:
  ```bash
  pip uninstall -y onc;
  pip install -U git+git://github.com/FlyingAndrew/api-python-client.git@master```
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

