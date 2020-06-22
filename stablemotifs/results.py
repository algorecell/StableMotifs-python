
import os

import pandas as pd

class StableMotifsResult(object):
    """
    TODO
    """

    def __init__(self, wd, model_name, fixed):
        """
        TODO
        """
        self.wd = wd
        self.model_name = model_name
        self.fixed = fixed
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

    def _parse_stable_motifs(self):
        inputf = self._wfile("%s-StableMotifs.txt")
        stable_motifs = []
        with open(inputf) as f:
            for sms in f.readlines():
                if not sms.strip():
                    continue
                smss=[(i.split('=')[0],int(i.split('=')[1])) for i in sms.strip().split('\t')]
                stable_motifs.append(dict(smss))
        return stable_motifs

    @property
    def stable_motifs(self):
        """
        TODO
        """
        if not hasattr(self, "_StableMotifsResult__cache_stable_motifs"):
            self.__cache_stable_motifs = self._parse_stable_motifs()
        return self.__cache_stable_motifs

    @property
    def control_sets(self):
        """
        TODO

        :rtype: dict[int, dict[str, int] list]
        """
        if not hasattr(self, "_StableMotifsResult__cache_control_sets"):
            self.__cache_control_sets = self._parse_control_sets()
        return self.__cache_control_sets

    def reprogramming_to_attractor(self, *spec, **kwspec):
        """
        TODO
        """
        strategies = ReprogrammingStrategies()
        spec = PartialState(*spec, **kwspec)
        for i, attractor in enumerate(self.attractors):
            if spec.match_state(attractor):
                for cs in self.control_sets[i]:
                    p = TemporaryPerturbation(cs)
                    s = FromCondition("input", p) if self.fixed else FromAny(p)
                    strategies.add(s)
        if self.fixed:
            strategies.register_alias("input", self.fixed)
        return strategies
