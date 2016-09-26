from pkg_resources import resource_filename
import json


__data__ = resource_filename("cltk_collatinus", "collatinus_data/collected.json")


class UnknownLemma(Exception):
    """ Exception raised on unknown lemma """


class LatinDecliner:
    def __init__(self):
        with open(__data__) as data_file:
            self.__data__ = json.load(data_file)

        self.__models__ = self.__data__["models"]
        self.__lemmas__ = self.__data__["lemmas"]

    def getRoots(self, lemma, roots=None):
        """

        :param lemma:
        :param roots:
        :return:
        """

        if lemma not in self.__lemmas__:
            raise UnknownLemma("%s is unknown" % lemma)

        returned_roots = {}
        lemma_entry = self.__lemmas__[lemma]
        if not roots:
            roots = self.__models__[lemma_entry["model"]]["R"]
        # For each registered root,
        for root_id, root_data in roots.items():
            # we get the real root specific to the lemma
            # They can be more than one (variants) splitted by ","
            lemma_roots = lemma_entry["lemma"]
            deletion, addition = int(root_data[0]), root_data[1]
            returned_roots[root_id] = [lemma_root[:-deletion] + addition for lemma_root in lemma_roots.split(",")]
        return returned_roots

    def decline(self, lemma):
        """

        :param lemma:
        :return:
        """

        if lemma not in self.__lemmas__:
            raise UnknownLemma("%s is unknown" % lemma)

        # Get data information
        lemma_entry = self.__lemmas__[lemma]
        model = self.__models__[lemma_entry["model"]]

        # Get the roots
        roots = self.getRoots(lemma, roots=model["R"])

        # Get the known forms in order
        keys = sorted([int(key) for key in model["des"].keys()])
        forms_data = [(key, model["des"][str(key)]) for key in keys]

        # Generate the return dict
        forms = {key: [] for key in keys}
        for key, form in forms_data:
            root_id, endings = tuple(form)
            for root in roots[root_id]:
                for ending in endings:
                    forms[key].append(root + ending)

        return forms


if __name__ == "__main__":
    import unittest

    class TestDecliner(unittest.TestCase):
        def setUp(self):
            self.decliner = LatinDecliner()

        def test_lemmatize(self):
            """ Ensure lemmatization works well """
            self.assertEqual(
                self.decliner.decline("via"),
                {1: ['via'], 2: ['via'], 3: ['viam'], 4: ['viae'], 5: ['viae'], 6: ['via'], 7: ['viae'],
                 8: ['viae'], 9: ['vias'], 10: ['viarum'], 11: ['viis'], 12: ['viis']},
                "Declination of via should be right"
            )
            self.assertEqual(
                self.decliner.decline("doctus"),
                {13: ['doctus'], 14: ['docte'], 15: ['doctum'], 16: ['docti'], 17: ['docto'], 18: ['docto'],
                 19: ['docti'], 20: ['docti'], 21: ['doctos'], 22: ['doctorum'], 23: ['doctis'], 24: ['doctis'],
                 25: ['docta'], 26: ['docta'], 27: ['doctam'], 28: ['doctae'], 29: ['doctae'], 30: ['docta'],
                 31: ['doctae'], 32: ['doctae'], 33: ['doctas'], 34: ['doctarum'], 35: ['doctis'], 36: ['doctis'],
                 37: ['doctum'], 38: ['doctum'], 39: ['doctum'], 40: ['docti'], 41: ['docto'], 42: ['docto'],
                 43: ['docta'], 44: ['docta'], 45: ['docta'], 46: ['doctorum'], 47: ['doctis'], 48: ['doctis'],
                 49: ['doctior'], 50: ['doctior'], 51: ['doctiorem'], 52: ['doctioris'], 53: ['doctiori'],
                 54: ['doctiore'], 55: ['doctiores'], 56: ['doctiores'], 57: ['doctiores'], 58: ['doctiorum'],
                 59: ['doctioribus'], 60: ['doctioribus'], 61: ['doctior'], 62: ['doctior'], 63: ['doctiorem'],
                 64: ['doctioris'], 65: ['doctiori'], 66: ['doctiore'], 67: ['doctiores'], 68: ['doctiores'],
                 69: ['doctiores'], 70: ['doctiorum'], 71: ['doctioribus'], 72: ['doctioribus'], 73: ['doctius'],
                 74: ['doctius'], 75: ['doctius'], 76: ['doctioris'], 77: ['doctiori'], 78: ['doctiore'],
                 79: ['doctiora'], 80: ['doctiora'], 81: ['doctiora'], 82: ['doctiorum'], 83: ['doctioribus'],
                 85: ['doctissimus'], 86: ['doctissime'], 87: ['doctissimum'], 88: ['doctissimi'], 89: ['doctissimo'],
                 90: ['doctissimo'], 91: ['doctissimi'], 92: ['doctissimi'], 93: ['doctissimos'], 94: ['doctissimorum'],
                 95: ['doctissimis'], 96: ['doctissimis'], 97: ['doctissima'], 98: ['doctissima'], 99: ['doctissimam'],
                 100: ['doctissimae'], 101: ['doctissimae'], 102: ['doctissima'], 103: ['doctissimae'],
                 104: ['doctissimae'], 105: ['doctissimas'], 106: ['doctissimarum'], 107: ['doctissimis'],
                 108: ['doctissimis'], 109: ['doctissimum'], 110: ['doctissimum'], 111: ['doctissimum'],
                 112: ['doctissimi'], 113: ['doctissimo'], 114: ['doctissimo'], 115: ['doctissima'],
                 116: ['doctissima'], 117: ['doctissima'], 118: ['doctissimorum'], 119: ['doctissimis'],
                 120: ['doctissimis']},
                "Doctus has three radicals and lots of forms"
            )
            print(self.decliner.decline("verbex"))

        def test_get_roots(self):
            """ Ensure roots are well constructed """
            self.assertEqual(
                self.decliner.getRoots("vita"), {"1": ["vit"]},
                "Vita has only one root : vit [Remove 1 char]"
            )
            self.assertEqual(
                self.decliner.getRoots("epulae"), {"1": ["epul"]},
                "Epulae has only one root : epul [Remove > 1 char]"
            )
            self.assertEqual(
                self.decliner.getRoots("doctus"),
                {"0": ["doct"], "1": ["docti"], "2": ["doctissim"]},
                "Doctus has three roots : doct, docti, doctissim [Remove > 1 char, Add > 1 char]"
            )
            self.assertEqual(
                self.decliner.getRoots("amo"),
                {"0": ["am"], "1": ["amau"], "2": ["amat"]},
                "Amo has three roots : am, amau, amat [Remove > 1 char, Add > 1 char]"
            )

    unittest.main()