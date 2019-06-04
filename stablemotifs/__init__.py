
import atexit
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd

from colomoto_jupyter.io import ensure_localfile

__version__ = "0.1"

STABLEMOTIFS_JAR = os.path.join(os.path.dirname(__file__), "jars",
        "StableMotifs.jar")


class StableMotifsResult(object):

    def __init__(self, wd, model_name, cleanup_wd=False):
        self.wd = wd
        self.model_name = model_name
        self.attractors = self._parse_attractors()

    def _wfile(self, pattern):
        return os.path.join(self.wd, pattern%self.model_name)

    def _parse_attractors(self):
        inputf = self._wfile("%s-QuasiAttractors.txt")
        df = pd.read_csv(inputf, sep='\t', index_col=-1) #index_col=-1 we cheat by making the extra tabs at the end of the rows in the files as the index column, and then resetting it to just natural incrementing integers
        df.reset_index(inplace=True,drop=True)
        d = df.to_dict("index")
        return [d[i] for i in range(len(d))]

    def _parse_control_sets(self):
        inputf = self._wfile("%s-StableMotifControlSets.txt")
        control_sets = dict([(i, []) for i in range(len(self.attractors))])
        with open(inputf) as f:
            for c in f.readlines():
                if not c:
                    continue
                cc=c.split('\t')[0]
                cd=[(i.split('=')[0],int(i.split('=')[1])) for i in cc.split(' ')]
                attr=c.split('\t')[1]
                attr_id = int(attr[9:])
                control_sets[attr_id].append(dict(sorted(cd)))
        return control_sets

    @property
    def control_sets(self):
        if not hasattr(self, "_StableMotifsResult__cache_control_sets"):
            self.__cache_control_sets = self._parse_control_sets()
        return self.__cache_control_sets


def load(modelfile, quiet=False):
    """
    Execute StableMotifs analysis on the given Boolean network model.

    :param str modelfile: Filename or URL of Boolean network in BooleanNet format
    :keyword bool quiet: If True, skip computation output
    :returns: :py:class:`.StableMotifsResult` instance
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

