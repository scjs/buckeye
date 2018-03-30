This package is for iterating through the
`Buckeye Corpus <http://buckeyecorpus.osu.edu/>`__ annotations in Python. It
uses the annotation timestamps to cross-reference the .words, .phones, and
.log files, and can be used to extract sound clips from the .wav files. It is
tested to work with Python 2.7 and 3.6.

Usage
-----

There is a short guide to using the package in the
`Quickstart <https://nbviewer.jupyter.org/github/scjs/buckeye/blob/master/Quickstart.ipynb>`__
notebook, and the docstrings in ``buckeye.py``, ``containers.py``, and
``utterance.py`` have more detail.

Installation
------------

The package can be installed from PyPI with pip with this command:

::

    pip install buckeye

The latest version can also be installed from GitHub with pip with this
command:

::

    pip install git+http://github.com/scjs/buckeye.git

You can also copy the ``buckeye`` subdirectory into your working
directory, or put it in your Python path.

Tests
-----

To run the tests, run ``nosetests`` from the root directory, or
``python setup.py test`` to install the test dependencies first.

References
----------

Pitt, M.A., Dilley, L., Johnson, K., Kiesling, S., Raymond, W., Hume, E.
and Fosler-Lussier, E. (2007) Buckeye Corpus of Conversational Speech
(2nd release) [www.buckeyecorpus.osu.edu] Columbus, OH: Department of
Psychology, Ohio State University (Distributor).
