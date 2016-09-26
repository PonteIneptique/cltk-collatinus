import json
import re
from copy import deepcopy
import unicodedata


def normalize_unicode(lines):
    return unicodedata.normalize('NFKD', lines).encode('ASCII', 'ignore').decode()


#############################################################
# Convert morphos.la
# Each line of Morphos.la represents a declension name
#############################################################
morphs_name = {}
with open("./cltk_collatinus/collatinus_data/src/morphos.la") as f:
    for index, line in enumerate(f.readlines()):
        morphs_name[index+1] = line.strip()

assert morphs_name[190] == "vocatif masculin singulier participe présent actif"

#############################################################
# Convert modeles.la
# Line starting with $ are variable that can be reused
# Set of line starting with model are models
# R:int:int,int (Root number, Character to remove to get canonical form, number of character to add to get the root)
#  -> eg. : for uita, R:1:1,0 would get root 1, 1 character to remove, 0 to add -> uit
#  -> eg. : for epulae, R:1:2,0 would get root 1, 2 character to remove, 0 to add : epul
#############################################################


def parse_range(des_number):
    """ Range

    :return: Int reprenting element of the range
    """
    ids = []
    for des_group in des_number.split(","):  # When we have ";", we should parse it normally
        if "-" in des_group:
            start, end = tuple([int(x) for x in des_group.split("-")])
            ids += list(range(start, end + 1))
        else:
            ids += [int(des_group)]
    return ids


def convert_models(lines, normalize=False):
    models = {}
    __model = {
        "R": {},
        "abs": [],  # Unused desinence if inherits
        "des": {},  # Dict of desinences
        "suf": {},  # Dict of Suffixes
        "sufd": []  # Possible endings
    }
    __R = re.compile("^R:(?P<root>\d+):(?P<remove>\w+)[,:]?(?P<add>\w+)?", flags=re.UNICODE)
    __des = re.compile("^des[\+]?:(?P<range>[\d\-,]+):(?P<root>\d+):([\w\-,;]+)$", flags=re.UNICODE)
    last_model = None
    variable_replacement = {}

    if normalize:
        lines = "\n".join(lines)
        lines = normalize_unicode(lines)
        lines = lines.split("\n")

    for lineno, line in enumerate(lines):
        line = line.strip()
        # If we get a variable
        if line.startswith("$"):
            # We split the line on =
            var, rep = tuple(line.split("="))
            # We create a replacement variable
            variable_replacement[var] = rep
        elif len(line) > 0 and not line.startswith("!"):
            if line.startswith("modele:"):
                last_model = line[7:]
                models[last_model] = deepcopy(__model)
            elif line.startswith("pere:"):
                # Inherits from parent
                models[last_model].update(
                    deepcopy(models[line[5:]])
                )
            elif line.startswith("R:"):
                # Still do not know how to deal with "K"
                root, remove, chars = __R.match(line).groups()
                if chars == "0":
                    chars = ""
                models[last_model]["R"][root] = [remove, chars]
            elif line.startswith("des"):
                # We have new endings
                # des:range:root_number:list_of_des
                # First we apply desinence variables replacement
                if "$" in line:
                    for var, rep in variable_replacement.items():
                        # First we replace +$
                        line = re.sub(
                            "(\w+)(\+\{})".format(var),
                            lambda x: (
                                ";".join([x.group(1) + r for r in rep.split(";")])
                            ),
                            line, flags=re.UNICODE
                        )
                        line = line.replace(var, rep)
                        if "$" not in line:
                            break
                des_number, root, des = __des.match(line).groups()

                ids = parse_range(des_number)
                for i, d in zip(ids, des.split(";")):
                    models[last_model]["des"][int(i)] = (root, d.replace("-", "").split(","))
            elif line.startswith("abs:"):
                models[last_model]["abs"] = parse_range(line[4:])  # Add the one we should not find as desi
            elif line.startswith("suf:"):
                rng, suf = tuple(line[4:].split(":"))
                models[last_model]["suf"] = {i: suf for i in parse_range(rng)}  # Sufd are suffix always present
            elif line.startswith("sufd:"):
                models[last_model]["sufd"] = line[5:]  # Sufd are suffix always present. Can has alternative
            else:
                print(line.split(":")[0])
    return models


with open("./cltk_collatinus/collatinus_data/src/modeles.la") as f:
    lines = f.read().split("\n")
    models = convert_models(lines)
    norm_models = convert_models(lines, True)


assert models["fortis"]["des"][13] == ("4", ['']),\
    "Root 4, Empty string (originally '-'), found %s %s" % models["fortis"]["des"][13]
assert models["fortis"]["des"][51] == ("1", ["ĭōrĕm"]),\
    "Root 4, Empty string (originally '-') found %s %s" % models["fortis"]["des"][50]

assert norm_models["fortis"]["des"][13] == ("4", ['']),\
    "Root 4, Empty string (originally '-'), found %s %s" % norm_models["fortis"]["des"][13]
assert norm_models["fortis"]["des"][51] == ("1", ["iorem"]),\
    "Root 4, Empty string (originally '-') found %s %s" % norm_models["fortis"]["des"][50]

############################################
#
#   Get the lemma converter
#
# lemma=lemma|model|genitive/infectum|perfectu|morpho indications
#
############################################

def parseLemma(lines, normalize=False):
    """

    :param lines:
    :param normalize:
    :return:
    """

    lemmas = {}
    regexp = re.compile("^(?P<lemma>\w+){1}(?P<quantity>\=\w+)?\|(?P<model>\w+)?\|[-]*(?P<geninf>[\w,]+)?[-]*\|[-]*(?P<perf>[\w,]+)?[-]*\|(?P<lexicon>.*)?", flags=re.UNICODE)

    if normalize:
        lines = "\n".join(lines)
        lines = normalize_unicode(lines)
        lines = lines.split("\n")

    for lineno, line in enumerate(lines):
        if not line.startswith("!") and "|" in line:
            if line.count("|") != 4:
                # We need to clean up the mess
                # Some line lacks a |
                # I assume this means we need to add as many before the dictionary
                should_have = 4
                missing = should_have - line.count("|")
                last_one = line.rfind("|")
                line = line[:last_one] + "|" * missing + line[last_one:]
            result = regexp.match(line)
            if not result:
                print(line)
            else:
                result = result.groupdict(default=None)
                # we always normalize the key
                lemmas[normalize_unicode(result["lemma"])] = result
    return lemmas

with open("./cltk_collatinus/collatinus_data/src/lemmes.la") as f:
    lines = f.read().split("\n")
    lemmas = parseLemma(lines, True)


assert lemmas["volumen"]["geninf"] == "volumin"
assert lemmas["volumen"]["lemma"] == "volumen"
assert lemmas["volumen"]["model"] == "corpus"

with open("./cltk_collatinus/collatinus_data/collected.json", "w") as f:
    json.dump(
        {
            "morph-name": morphs_name,
            "scansions": {
                "models": models
            },
            "models": norm_models,
            "lemmas": lemmas
        },
        f
    )