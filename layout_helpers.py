from math import floor

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

def collides_with(prev_event, curr_event):
    if prev_event["end"] > curr_event["start"]:
        return True
    return False

def calc_padding_and_height(daylist):
    padding = []
    height = []

    for event, i in zip(daylist, range(len(daylist))):
        start = event["start"]
        end = event["end"]

        if i == 0:
            delta_padding = start - start.replace(hour=0, minute=0)
        else:
            delta_padding = start - daylist[i-1]["end"]
    
        padding.append(int(timedelta_to_cell_height(delta_padding)))

        delta_height = end - start
        height.append(timedelta_to_cell_height(delta_height))

    return [height, padding]


def timedelta_to_cell_height(timedelta, hour_height=4):
    sec = timedelta.seconds
    
    hours = (floor(sec/3600)) * hour_height
    minutes = round_resolution((1/60) * ((sec/60)%60)) * hour_height

    return hours + minutes


def round_resolution(value, resolution=0.25):
    # rounds to resolution e.g. round_resolution(4.33) = 4.25
    return round(value/resolution) * resolution

# TODO: remove, just for testing atm
if __name__ == "__main__":
    print(calc_padding_and_height([]))