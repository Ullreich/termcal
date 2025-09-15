from math import floor

from icalendar import Event

from textual.app import App

from typing import List


def overlap_list(daylist: List[Event]) -> List[List[Event]]:
    """Return columns of non-overlapping icalendar.Event components.

    Filters out any items that are not VEVENTs or that are missing DTSTART/DTEND/UID,
    so downstream code (EventCell) can rely on SUMMARY/UID existing.
    """
    # Keep only proper VEVENTs with required properties
    events: List[Event] = [
        e for e in daylist
        if isinstance(e, Event)
        and e.get("DTSTART") is not None
        and e.get("DTEND") is not None
        and e.get("UID") is not None
    ]
    if not events:
        return []

    # Sort chronologically by DTSTART
    events.sort(key=lambda e: getattr(e.get("DTSTART"), "dt", None))

    columns: List[List[Event]] = []
    for ev in events:
        placed = False
        for col in columns:
            if not collides_with(col[-1], ev):
                col.append(ev)
                placed = True
                break
        if not placed:
            columns.append([ev])

    return columns


def collides_with(prev_event: Event, curr_event: Event) -> bool:
    prev_dtend_prop = prev_event.get("DTEND")
    curr_dtstart_prop = curr_event.get("DTSTART")
    if prev_dtend_prop is None or curr_dtstart_prop is None:
        return False
    prev_dtend = getattr(prev_dtend_prop, "dt", None)
    curr_dtstart = getattr(curr_dtstart_prop, "dt", None)
    if prev_dtend is None or curr_dtstart is None:
        return False
    return prev_dtend > curr_dtstart


def calc_padding_and_height(daylist: List[Event]):
    padding = []
    height = []

    for event, i in zip(daylist, range(len(daylist))):
        start = event.get("DTSTART").dt
        end = event.get("DTEND").dt

        if i == 0:
            delta_padding = start - start.replace(hour=0, minute=0)
        else:
            delta_padding = start - daylist[i-1].get("DTEND").dt
    
        padding.append(int(timedelta_to_cell_height(delta_padding)))

        delta_height = end - start
        height.append(timedelta_to_cell_height(delta_height))

    return [height, padding]


def timedelta_to_cell_height(timedelta, hour_height=4):
    sec = timedelta.seconds
    
    hours = (floor(sec/3600)) * hour_height
    minutes = round_resolution((1/60) * ((sec/60)%60)) * hour_height

    return max(hours + minutes, 1)


def round_resolution(value, resolution=0.25):
    # rounds to resolution e.g. round_resolution(4.33) = 4.25
    return round(value/resolution) * resolution

def pop_all_screens(main_app: App, depth = 1) -> None:
    while len(main_app.screen_stack)>depth:
        main_app.pop_screen()

def refresh_and_restore_scroll(main_app: App) -> None:
    from weekview.WeekGrid import WeekGrid
    wg = main_app.query_one(WeekGrid)
    y = wg.vscroll.scroll_y
    wg.refresh(recompose=True)
    wg.call_after_refresh(lambda: wg.vscroll.scroll_to(y=y, animate=False))

# TODO: remove, just for testing atm
if __name__ == "__main__":
    print(calc_padding_and_height([]))