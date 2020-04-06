
import atexit
import os
import shutil
import subprocess
import sys
import tempfile

from colomoto_jupyter import import_colomoto_tool
from colomoto_jupyter.io import ensure_localfile

from .jupyter import upload

__version__ = "0.1"

STABLEMOTIFS_JAR = os.path.join(os.path.dirname(__file__), "jars",
        "StableMotifs.jar")

from .results import StableMotifsResult

def load(model, mcl="", msm="", quiet=False):
    """
    Execute StableMotifs analysis on the given Boolean network model.

    :param biolqm or str modelfile: either a bioLQM object, or Filename/URL of Boolean network in BooleanNet format
    :param str mcl: Optional parameter for a threshold in the maximum cycle length (mcl). One must specify both a mcl and msm.
    :param str msm: Optional parameter for a threshold in the maximum stable motif size (msm).  One must specify both a mcl and msm.
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
        modelfile = os.path.join(wd, "model.txt")
        assert biolqm.save(model, modelfile, "booleannet"), "Error converting from bioLQM"
        return modelfile, False

    is_modelfile = True
    if "biolqm" in sys.modules:
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
        shutil.copy(modelfile, wd)

    modelbase = os.path.basename(modelfile)
    model_name = modelbase.split(".")[0]

    # invoke StableMotifs
    argv = ["java", "-jar", STABLEMOTIFS_JAR, modelbase]
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
    return StableMotifsResult(wd, model_name)

