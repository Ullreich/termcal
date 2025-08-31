def overlap_list(daylist):
    ret = []
    daycopy = daylist.copy()
    if len(daylist) == 0:
        return []

    for event in daylist:
        # if the list is still empty, we just add the event, no collisions possible
        if (len(ret) == 0) or (not collides_with(ret[-1], event)):
            ret.append(event)
            daycopy.remove(event)

    return [ret] + overlap_list(daycopy)

def write_overlap_list(overlap):
    # TODO: recusrively call until daylist is empty
    for ret in overlap:
        with open("overlap_test.txt", "a") as f:
            # f.write("og\n")
            f.write(f"{[x["summary"][:10] for x in ret]} \n")
            # f.write(f"{ret} \n")
    
    with open("overlap_test.txt", "a") as f:
        f.write("\n")

def write_overlap_list(overlap):
    # TODO: recusrively call until daylist is empty
    with open("overlap_test.txt", "a") as f:
        f.write(f"{overlap}")
        f.write("\n")

def collides_with(prev_event, curr_event):
    if prev_event["end"] > curr_event["start"]:
        return True
    return False