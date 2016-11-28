This package has Python classes for iterating through the annotations
in the [Buckeye Corpus](http://buckeyecorpus.osu.edu/). They provide 
cross-references between the .words, .phones, and .log files, and
can be used to extract sound clips from the .wav files.

Usage
-----
There is a short guide to using the package in the 
[Quickstart](https://nbviewer.jupyter.org/github/scjs/buckeye/blob/master/Quickstart.ipynb)
notebook, and the docstrings in `buckeye.py`, `containers.py`, and
`utterance.py` have more detail.

Installation
------------
The package can be installed from GitHub with pip using this command:

    pip install git+http://github.com/scjs/buckeye.git

You can also copy the `buckeye/` subdirectory into your working directory, or
put it in your Python path.

Tests
-----
To run the tests, run `nosetests` from the root directory, or
`python setup.py test` to install the test dependencies first. The package
is tested to work with Python 2.7 and 3.5.