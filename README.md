This repository has Python classes for iterating through the annotations
in the [Buckeye Corpus](http://buckeyecorpus.osu.edu/). They include 
cross-references between the .words, .phones, and .log files, and
can be used to extract sound clips from the .wav files.

The scripts can be installed directly from GitHub with pip using this command:

    pip install git+http://github.com/scjs/buckeye.git

You can also copy the `buckeye/` subdirectory into your working directory, or
put it in your Python path.

There is a short guide to using the package in the QuickStart notebook, and
the docstrings in buckeye.py and containers.py have more detail.
