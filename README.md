# StableMotifs-python

This module brings a Python interface to the tool [StableMotifs](https://github.com/jgtz/StableMotifs) (Jorge G. T.  Zañudo and Réka Albert),
for the control of Boolean networks.

The control predictions can be processed using the [algorecell_types](https://github.com/algorecell/algorecell_types) library, which eases the
display and comparison with other control methods.

## Installation

<!--
### CoLoMoTo Notebook environment

`stablemotifs-python` is distributed as part of the [CoLoMoTo docker](http://colomoto.org/notebook).

-->

### Using conda
```
conda install -c colomoto stablemotifs-python
```

### Using pip

```
pip install stablemotifs
python -m stablemotifs_setup
```

## Documentation

Documentation is available at https://stablemotifs-python.readthedocs.io.

Examples can be found at:
* https://nbviewer.jupyter.org/github/algorecell/StableMotifs-python/tree/master/examples/

### Quick usage

```py
>>> import stablemotifs
```

Model loading:

```py
>>> sm = stablemotifs.load("network.txt") # in BooleanNet format
# alternatively, load with biolqm in any format
>>> import biolqm
>>> lm = biolqm.load("model.zginml") # or any format support by bioLQM
>>> sm = stablemotifs.load(lm)
```

Reprogramming predictions:

```py
>>> sr = sm.reprogramming_to_attractor({"A": 1, "B": 0})
>>> sr.as_table()
```

See ``help(sr)`` for other display methods

