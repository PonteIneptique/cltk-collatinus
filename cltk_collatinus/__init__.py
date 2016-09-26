""" This modules provides Decliner for Latin. Given a lemma, the Decliner will provide each grammatically valid forms

This work is based on the lexical and linguistic data built for and by the Collatinus Team ( https://github.com/biblissima/collatinus ).
This module hence inherit the license from the original project. The objective of this module is to port part of Collatinus to CLTK.

"""

__author__ = "Thibault Clerice, Yves Ouvrard and Philippe Verkerk"
__license__ = "GNU GENERAL PUBLIC LICENSE, 2007"
__credits__ = ["Thibault Clerice", "Yves Ouvrard", "Philippe Verkerk"]

from pkg_resources import resource_filename
import json


__data__ = resource_filename("cltk_collatinus", "collatinus_data/collected.json")


class UnknownLemma(Exception):
    """ Exception raised on unknown lemma """


class LatinDecliner:
    """

    """
    def __init__(self):
        with open(__data__) as data_file:
            self.__data__ = json.load(data_file)

        self.__models__ = self.__data__["models"]
        self.__lemmas__ = self.__data__["lemmas"]

    def getRoots(self, lemma, model_roots=None):
        """ Retrieve the known roots of a lemma

        :param lemma: Canonical form of the word (lemma)
        :type lemma: str
        :param model_roots: I
        :return: Dictionary of roots with their root identifier as key
        :rtype: dict
        """

        if lemma not in self.__lemmas__:
            raise UnknownLemma("%s is unknown" % lemma)

        ROOT_IDS = {
            "K": "lemma",
            "1": "geninf",
            "2": "perf"
        }

        lemma_entry = self.__lemmas__[lemma]
        original_roots = {
            root_id: lemma_entry[root_name].split(",")
            for root_id, root_name in ROOT_IDS.items()
            if root_id != "K" and lemma_entry[root_name]
        }
        returned_roots = {}

        if not model_roots:
            model_roots = self.__models__[lemma_entry["model"]]["R"]

        # For each registered root in the model,
        for model_root_id, model_root_data in model_roots.items():

            # If we have K, it's equivalent to canonical form
            if model_root_data[0] == "K":
                returned_roots[model_root_id] = [lemma_entry["lemma"]]
            # Otherwise we have deletion number and addition char
            else:
                deletion, addition = int(model_root_data[0]), model_root_data[1]

                # If a the root is declared already,
                # we retrieve the information
                if model_root_id != "1" and model_root_id in returned_roots:
                    lemma_roots = returned_roots[model_root_id]
                else:
                    lemma_roots = lemma_entry["lemma"].split(",")

                returned_roots[model_root_id] = [
                    lemma_root[:-deletion] + addition
                    for lemma_root in lemma_roots
                ]

        # We update with the new roots
        original_roots.update(returned_roots)
        return original_roots

    def decline(self, lemma, flatten=False):
        """ Decline a lemma

        :raise UnknownLemma: When the lemma is unknown to our data

        :param lemma: Lemma (Canonical form) to decline
        :type lemma: str
        :param flatten: If set to True, returns a list of forms without natural language information about them
        :return: Dictionary of grammatically valid forms, including variants, with keys corresponding to morpho informations.
        :rtype: list or dict
        """

        if lemma not in self.__lemmas__:
            raise UnknownLemma("%s is unknown" % lemma)

        # Get data information
        lemma_entry = self.__lemmas__[lemma]
        model = self.__models__[lemma_entry["model"]]

        # Get the roots
        roots = self.getRoots(lemma, model_roots=model["R"])

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

        if flatten:
            return list([form for case_forms in forms.values() for form in case_forms])
        return forms


if __name__ == "__main__":
    import unittest

    class TestDecliner(unittest.TestCase):
        def setUp(self):
            self.decliner = LatinDecliner()

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

        def test_decline(self):
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
            self.assertEqual(
                self.decliner.decline("verbex"),
                {1: ['verbex'], 2: ['verbex'], 3: ['verbicem'], 4: ['verbicis'], 5: ['verbici'], 6: ['verbice'],
                 7: ['verbices'], 8: ['verbices'], 9: ['verbices'], 10: ['verbicum'], 11: ['verbicibus'],
                 12: ['verbicibus']},
                "Verbex has two different roots : checking they are taken into account"
            )
            self.assertEqual(
                self.decliner.decline("vendo"),
                {121: ['vendo'], 122: ['vendis'], 123: ['vendit'], 124: ['vendimus'], 125: ['venditis'],
                 126: ['vendunt'], 127: ['vendebam'], 128: ['vendebas'], 129: ['vendebat'], 130: ['vendebamus'],
                 131: ['vendebatis'], 132: ['vendebant'], 133: ['vendam'], 134: ['vendes'], 135: ['vendet'],
                 136: ['vendemus'], 137: ['vendetis'], 138: ['vendent'], 139: ['vendaui'], 140: ['vendauisti'],
                 141: ['vendauit'], 142: ['vendauimus'], 143: ['vendauistis'], 144: ['vendauerunt', 'vendauere'],
                 145: ['vendaueram'], 146: ['vendaueras'], 147: ['vendauerat'], 148: ['vendaueramus'],
                 149: ['vendaueratis'], 150: ['vendauerant'], 151: ['vendauero'], 152: ['vendaueris'],
                 153: ['vendauerit'], 154: ['vendauerimus'], 155: ['vendaueritis'], 156: ['vendauerint'],
                 157: ['vendam'], 158: ['vendas'], 159: ['vendat'], 160: ['vendamus'], 161: ['vendatis'],
                 162: ['vendant'], 163: ['venderem'], 164: ['venderes'], 165: ['venderet'], 166: ['venderemus'],
                 167: ['venderetis'], 168: ['venderent'], 169: ['vendauerim'], 170: ['vendaueris'], 171: ['vendauerit'],
                 172: ['vendauerimus'], 173: ['vendaueritis'], 174: ['vendauerint'], 175: ['vendauissem'],
                 176: ['vendauisses'], 177: ['vendauisset'], 178: ['vendauissemus'], 179: ['vendauissetis'],
                 180: ['vendauissent'], 181: ['vende'], 182: ['vendite'], 183: ['vendito'], 184: ['vendito'],
                 185: ['venditote'], 186: ['vendunto'], 187: ['vendere'], 188: ['vendasse'], 189: ['vendens'],
                 190: ['vendens'], 191: ['vendentem'], 192: ['vendentis'], 193: ['vendenti'], 194: ['vendente'],
                 195: ['vendentes'], 196: ['vendentes'], 197: ['vendentes'], 198: ['vendentium', 'vendentum'],
                 199: ['vendentibus'], 200: ['vendentibus'], 201: ['vendens'], 202: ['vendens'], 203: ['vendentem'],
                 204: ['vendentis'], 205: ['vendenti'], 206: ['vendente'], 207: ['vendentes'], 208: ['vendentes'],
                 209: ['vendentes'], 210: ['vendentium', 'vendentum'], 211: ['vendentibus'], 212: ['vendentibus'],
                 213: ['vendens'], 214: ['vendens'], 215: ['vendens'], 216: ['vendentis'], 217: ['vendenti'],
                 218: ['vendente'], 219: ['vendentia'], 220: ['vendentia'], 221: ['vendentia'],
                 222: ['vendentium', 'vendentum'], 223: ['vendentibus'], 224: ['vendentibus'], 225: ['vendaturus'],
                 226: ['vendature'], 227: ['vendaturum'], 228: ['vendaturi'], 229: ['vendaturo'], 230: ['vendaturo'],
                 231: ['vendaturi'], 232: ['vendaturi'], 233: ['vendaturos'], 234: ['vendaturorum'],
                 235: ['vendaturis'], 236: ['vendaturis'], 237: ['vendatura'], 238: ['vendatura'], 239: ['vendaturam'],
                 240: ['vendaturae'], 241: ['vendaturae'], 242: ['vendatura'], 243: ['vendaturae'], 244: ['vendaturae'],
                 245: ['vendaturas'], 246: ['vendaturarum'], 247: ['vendaturis'], 248: ['vendaturis'],
                 249: ['vendaturum'], 250: ['vendaturum'], 251: ['vendaturum'], 252: ['vendaturi'], 253: ['vendaturo'],
                 254: ['vendaturo'], 255: ['vendatura'], 256: ['vendatura'], 257: ['vendatura'], 258: ['vendaturorum'],
                 259: ['vendaturis'], 260: ['vendaturis'], 261: ['vendendum'], 262: ['vendendi'], 263: ['vendendo'],
                 264: ['vendendo'], 265: ['vendatum'], 266: ['vendatu'], 267: ['vendor'], 268: ['venderis', 'vendere'],
                 269: ['venditur'], 270: ['vendimur'], 271: ['vendimini'], 272: ['venduntur'], 273: ['vendebar'],
                 274: ['vendebaris', 'vendebare'], 275: ['vendebatur'], 276: ['vendebamur'], 277: ['vendebamini'],
                 278: ['vendebantur'], 279: ['vendar'], 280: ['venderis', 'vendere'], 281: ['vendetur'],
                 282: ['vendemur'], 283: ['vendemini'], 284: ['vendentur'], 285: ['vendar'], 286: ['vendaris'],
                 287: ['vendatur'], 288: ['vendamur'], 289: ['vendamini'], 290: ['vendantur'], 291: ['venderer'],
                 292: ['vendereris'], 293: ['venderetur'], 294: ['venderemur'], 295: ['venderemini'],
                 296: ['venderentur'], 297: ['vendere'], 298: ['vendimini'], 299: ['venditor'], 300: ['venditor'],
                 301: ['venduntor'], 302: ['vendi'], 303: ['vendatus'], 304: ['vendate'], 305: ['vendatum'],
                 306: ['vendati'], 307: ['vendato'], 308: ['vendato'], 309: ['vendati'], 310: ['vendati'],
                 311: ['vendatos'], 312: ['vendatorum'], 313: ['vendatis'], 314: ['vendatis'], 315: ['vendata'],
                 316: ['vendata'], 317: ['vendatam'], 318: ['vendatae'], 319: ['vendatae'], 320: ['vendata'],
                 321: ['vendatae'], 322: ['vendatae'], 323: ['vendatas'], 324: ['vendatarum'], 325: ['vendatis'],
                 326: ['vendatis'], 327: ['vendatum'], 328: ['vendatum'], 329: ['vendatum'], 330: ['vendati'],
                 331: ['vendato'], 332: ['vendato'], 333: ['vendata'], 334: ['vendata'], 335: ['vendata'],
                 336: ['vendatorum'], 337: ['vendatis'], 338: ['vendatis'], 339: ['vendendus'], 340: ['vendende'],
                 341: ['vendendum'], 342: ['vendendi'], 343: ['vendendo'], 344: ['vendendo'], 345: ['vendendi'],
                 346: ['vendendi'], 347: ['vendendos'], 348: ['vendendorum'], 349: ['vendendis'], 350: ['vendendis'],
                 351: ['vendenda'], 352: ['vendenda'], 353: ['vendendam'], 354: ['vendendae'], 355: ['vendendae'],
                 356: ['vendenda'], 357: ['vendendae'], 358: ['vendendae'], 359: ['vendendas'], 360: ['vendendarum'],
                 361: ['vendendis'], 362: ['vendendis'], 363: ['vendendum'], 364: ['vendendum'], 365: ['vendendum'],
                 366: ['vendendi'], 367: ['vendendo'], 368: ['vendendo'], 369: ['vendenda'], 370: ['vendenda'],
                 371: ['vendenda'], 372: ['vendendorum'], 373: ['vendendis'], 374: ['vendendis']},
                "Check verb vendo declines well"
            )
            self.assertEqual(
                self.decliner.decline("poesis"),
                {1: ['poesis'], 2: ['poesis'], 3: ['poesem'], 4: ['poesis'], 5: ['poesi'], 6: ['poese'], 7: ['poeses'],
                 8: ['poesin', 'poesim'], 9: ['poeseos'], 10: ['poesium'], 11: ['poesibus'], 12: ['poesibus']},
                "Duplicity of forms should be accepted"
            )

        def test_flatten_decline(self):
            """ Ensure that flattening decline result is consistant"""
            self.assertEqual(
                self.decliner.decline("via", flatten=True),
                ['via', 'via', 'viam', 'viae', 'viae', 'via', 'viae', 'viae', 'vias', 'viarum', 'viis', 'viis'],
                "Declination of via should be right"
            )
            self.assertEqual(
                self.decliner.decline("poesis", flatten=True),
                ['poesis', 'poesis', 'poesem', 'poesis', 'poesi', 'poese', 'poeses', 'poesin', 'poesim', 'poeseos',
                 'poesium', 'poesibus', 'poesibus'],
                "Duplicity of forms should be accepted"
            )


    unittest.main()
