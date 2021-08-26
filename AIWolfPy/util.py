def getTarget(text):
        if "Agent" in text:
            startIndex = text.index("[") + 1
            endIndex = text.index("]")
            return int(text[startIndex: endIndex])
        else:
            return None

# Relativize a dictionary, where the key is an agent and the value is the weight to be relativized
def relativize(dict):
    # get sum of current dict (excluding agents with weights < 0)
    tot = 0
    for value in dict.values():
        if value > 0:
            tot += value

    # relativise based on sum
    new_dict = {}
    # (excluding agents with weights < 0)
    for key in dict.keys():
        # (excluding agents with weights < 0)
        if dict[key] > 0:
            new_dict[key] = dict[key] / tot
        else:
            new_dict[key] = dict[key]
            