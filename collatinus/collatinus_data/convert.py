import json
import re
from copy import deepcopy

# Convert morphos.la
# Each line of Morphos.la represents a declension name
morphs_name = {}
with open("./collatinus/collatinus_data/src/morphos.la") as f:
    for index, line in enumerate(f.readlines()):
        morphs_name[index+1] = line.strip()

assert morphs_name[190] == "vocatif masculin singulier participe présent actif"

# Convert modeles.la
# Line starting with $ are variable that can be reused
# Set of line starting with model are models
# R:int:int,int (Root number, Character to remove to get canonical form, number of character to add to get the root)
#  -> eg. : for uita, R:1:1,0 would get root 1, 1 character to remove, 0 to add -> uit
#  -> eg. : for epulae, R:1:2,0 would get root 1, 2 character to remove, 0 to add : epul

models = {}
__model = {
    "R": {},
    "abs": [],  # Unused desinence if inherits
    "des": {}
}
__R = re.compile("^R:(?P<root>\d+):(?P<remove>\w+)[,:]?(?P<add>\w+)?", flags=re.UNICODE)
__des = re.compile("^des:(?P<range>[\d\-,]+):(?P<root>\d+):([\w\-,;]+)$", flags=re.UNICODE)


with open("./collatinus/collatinus_data/src/modeles.la") as f:
    last_model = None
    variable_replacement = {}
    for line in f.readlines():
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
                    models[line[5:]]
                )
            elif line.startswith("R:"):
                # Still do not know how to deal with "K"
                root, remove, chars = __R.match(line).groups()
                models[last_model]["R"][root] = [remove, chars]
            elif line.startswith("des:"):
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
                if not __des.match(line):
                    print(line)
                des_number, root, des = __des.match(line).groups()

                ids = []
                for des_group in des_number.split(","):  # When we have ";", we should parse it normally
                    if "-" in des_group:
                        start, end = tuple([int(x) for x in des_group.split("-")])
                        ids += list(range(start, end+1))
                    else:
                        ids += [int(des_group)]
                for i, d in zip(ids, des.split(";")):
                    models[last_model]["des"][i] = d.split(",")

    print(models["uita"])
    print(models["epulae"])
    print(models["fortis"])