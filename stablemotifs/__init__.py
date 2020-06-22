"""
This module brings a Python interface to the tool `"StableMotifs"
<https://github.com/jgtz/StableMotifs>`_ (Jorge G. T.  Zañudo and Réka Albert),
for the control of Boolean networks.

The control predictions can be processed using the `algorecell_types
<https://github.com/algorecell/algorecell_types>`_ library, which eases the
display and comparison with other control methods.

Installation instructions at https://github.com/algorecell/StableMotifs-python

Quick usage:

>>> import stablemotifs

Model loading:

>>> sm = stablemotifs.load("network.txt") # in BooleanNet format
# alternatively, load with biolqm in any format
>>> import biolqm
>>> lm = biolqm.load("model.zginml") # or any format support by bioLQM
>>> sm = stablemotifs.load(lm)

Reprogramming predictions:

>>> sr = sm.reprogramming_to_attractor({"A": 1, "B": 0})
>>> sr.as_table()

See ``help(sr)`` for other display methods

Examples can be found at:
    * https://nbviewer.jupyter.org/github/algorecell/StableMotifs-python/tree/master/examples/

"""

import atexit
import os
import shutil
import subprocess
import sys
import tempfile

from colomoto_jupyter import import_colomoto_tool
from colomoto_jupyter.io import ensure_localfile

from colomoto.minibn import BooleanNetwork

from .jupyter import upload

from .results import StableMotifsResult

def load(model, fixed=None, mcl="", msm="", quiet=False):
    """
    Execute StableMotifs analysis on the given Boolean network model.

    :param model: either a ``biolqm`` or ``ginsim`` object, or filename/URL of Boolean network in BooleanNet format
    :keyword dict[str,int] fixed: fix the given nodes to their associated given values
    :keyword str mcl: Optional threshold in the maximum cycle length (mcl). One must specify both a mcl and msm.
    :keyword str msm: Optional threshold in the maximum stable motif size (msm).  One must specify both a mcl and msm.
    :keyword bool quiet: If True, skip computation output
    :rtype: :py:class:`.results.StableMotifsResult` instance
    """

    # prepare temporary working space
    wd = tempfile.mkdtemp(prefix="StableMotifs-")
    # cleanup working directory at exit
    def cleanup():
        shutil.rmtree(wd)
    atexit.register(cleanup)

    def biolqm_import(biolqm, lqm):
        if fixed:
            pert = " ".join((f"{node}%{value}" for node, value in fixed.items()))
            lqm = biolqm.perturbation(lqm, pert)
        modelfile = os.path.join(wd, "model.txt")
        assert biolqm.save(lqm, modelfile, "booleannet"), "Error converting from bioLQM"
        return modelfile, False

    is_modelfile = True
    if isinstance(model, BooleanNetwork):
        lqm = model.to_biolqm()
        biolqm = import_colomoto_tool("biolqm")
        modelfile, is_modelfile = biolqm_import(biolqm, lqm)
    elif "biolqm" in sys.modules:
        biolqm = sys.modules["biolqm"]
        if biolqm.is_biolqm_object(model):
            modelfile, is_modelfile = biolqm_import(biolqm, model)
    if is_modelfile and "ginsim" in sys.modules:
        ginsim = sys.modules["ginsim"]
        if ginsim.is_ginsim_object(model):
            model = ginsim.to_biolqm(model)
            biolqm = import_colomoto_tool("biolqm")
            modelfile, is_modelfile = biolqm_import(biolqm, model)

    if is_modelfile:
        modelfile = ensure_localfile(model)
        if fixed:
            biolqm = import_colomoto_tool("biolqm")
            model = biolqm.load(modelfile, "booleannet")
            modelfile, is_modelfile = biolqm_import(biolqm, model)
        else:
            shutil.copy(modelfile, wd)

    modelbase = os.path.basename(modelfile)
    model_name = modelbase.split(".")[0]

    # invoke StableMotifs
    argv = ["StableMotifs", modelbase]
    if mcl and msm:
        argv += list(map(str, [mcl, msm]))
    proc = subprocess.Popen(argv, cwd=wd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with proc.stdout:
        for line in iter(proc.stdout.readline, b''):
            if quiet:
                continue
            sys.stdout.write(line)
    assert proc.wait() == 0, "An error occured while running StableMotifs"

    # return interface to results
    return StableMotifsResult(wd, model_name, fixed)

