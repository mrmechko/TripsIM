import json
import copy

def loadont(pathName):
    # Put ontology in a dictionary so we can index by name of word
    ont = {}
    for i in json.load(open(pathName)):
        ont[i["name"]] = i

    # Precompute ancestory relationship
    for word, entry in ont.items():
        ancestors = []
        child = word
        ancestors.append(word)
        while ont[child]["parent"] != []:
            ancestors.append(ont[child]["parent"])
            child = ont[child]["parent"]
        ont[word]["ancestors"] = ancestors
        
    return ont

# Is a an ancestor of b?
def isAncestor(a, b):
    return a in ont[b]["ancestors"]

# Is a a child of b?
def isChild(a, b):
    return isAncestor(b, a)

# How far away is a from b?
def distance(a, b):
    ancestorsA, ancestorsB = copy.deepcopy(ont[a]["ancestors"]), copy.deepcopy(ont[b]["ancestors"])
    if a == b:
        return 0
    if a in ont[b]["ancestors"]:
        return ont[b]["ancestors"].index(a)
    if b in ont[a]["ancestors"]:
        return ont[a]["ancestors"].index(b)
    # First find lowest common ancestor
    ancestorsA.reverse()
    ancestorsB.reverse()
    i = 0
    while i < len(ancestorsA) and i < len(ancestorsB) and ancestorsA[i] == ancestorsB[i]:
        i += 1
    lowestCommonAncestor = ancestorsA[i-1]
    # Next compute distance of lowest ancestor to a and b, and add them
    return distance(a, lowestCommonAncestor) + distance(b, lowestCommonAncestor)


# Following class/functions not used for anything currently but probably will be useful
class Argument:
    def __init__(self, entry):
        self.role = entry["role"]
        self.restrictions = entry["restrictions"]
        self.optionality = entry["optionality"]
        self.implements = entry["implements"]

    def __repr__(self):
        return ("role: " + str(self.role) + ", restrictions: " + str(self.restrictions) + ", optionality: " + str(self.optionality) + ", implements: " + str(self.implements))

    def __eq__(self, other):
        return (self.role == other.role and self.restrictions == other.restrictions and self.optionality == other.optionality and self.implements == other.implements)

# Returns all of the arguments for a given entry
def getArguments(entry):
    return [Argument(x) for x in ont[entry]["arguments"]]


def test():
    assert isAncestor("MUSIC", "MELODY")
    assert isChild("MELODY", "MUSIC")
    assert distance("MELODY", "MUSIC-MOVEMENT") == 2
    assert distance("MELODY", "DEFINITION") == 4
    assert getArguments("FULLNAME") == [Argument(ont["FULLNAME"]["arguments"][0])]

ont = loadont("ontology.json")