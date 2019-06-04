
import atexit
import os
import shutil
import subprocess
import sys
import tempfile

from colomoto_jupyter.io import ensure_localfile

from .jupyter import upload

__version__ = "0.1"

STABLEMOTIFS_JAR = os.path.join(os.path.dirname(__file__), "jars",
        "StableMotifs.jar")

from .results import StableMotifsResult

def load(modelfile, quiet=False):
    """
    Execute StableMotifs analysis on the given Boolean network model.

    :param str modelfile: Filename or URL of Boolean network in BooleanNet format
    :keyword bool quiet: If True, skip computation output
    :returns: :py:class:`.results.StableMotifsResult` instance
    """
    modelfile = ensure_localfile(modelfile)
    modelbase = os.path.basename(modelfile)
    model_name = modelbase.split(".")[0]

    # prepare temporary working space
    wd = tempfile.mkdtemp(prefix="StableMotifs-")

    # cleanup working directory at exit
    def cleanup():
        shutil.rmtree(wd)
    atexit.register(cleanup)

    # copy model file
    shutil.copy(modelfile, wd)

    # invoke StableMotifs
    proc = subprocess.Popen(["java", "-jar", STABLEMOTIFS_JAR, modelbase],
        cwd=wd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with proc.stdout:
        for line in iter(proc.stdout.readline, b''):
            if quiet:
                continue
            sys.stdout.write(line)
    assert proc.wait() == 0, "An error occured while running StableMotifs"

    # return interface to results
    return StableMotifsResult(wd, model_name)

