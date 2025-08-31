# small/random stuff
- [ ] may need extra ical packages: https://icalendar.readthedocs.io/en/stable/#related-projects
- [ ] make links in description clickable: https://textual.textualize.io/widgets/link/#__tabbed_1_2
- [ ] make css reactive
- [ ] account for multi-day events
- [ ] how to properly add venv to git?
- [ ] set font size on start

# command line args
- [x] default date to today

# next/prev week
- [x] add key commands to go to next/prev week
- [ ] add way to write desired week into command?
- [x] change header to display current week

# alignment
- [x] think about how to best align/format the buttons
  - [x] perhaps no buttons for times without events?
  - [x] correctly size buttons based on duration
  - [ ] account for multi-day events
  - [ ] make resolution more modular/editable by user?
  - [ ] detatch day/time indicator and pin to top (along with overlapping event indicator?)
  - [ ] on start/switching of week, start at 8:00
  - [x] assert cell height at least 1
  - [ ] sort list of list of events by number of events in list

# coloring
- [x] add coloring for event through function that maps title to color?
  - [ ] depending on if light or dark color theme, edit function
- [ ] let person set color for event(s)

# tests
- [ ] add unittests

# add keyboard navigation
- [ ] add vim keybinds?
- [ ] add config file for keyboard binds?
- [ ] add screen that shows all key commands
- [ ] mouse button to escape from event view?

# cleanup/refactoring
- [ ] make all variables lower_case_with_underscores instead of CapitalizedWords
- [ ] rename some variables?
- [ ] make pep8 compliant: get vscode plugin

# implement calDav

# send push notifications

# bugs:
- [x] disable next and previous week when on eventScreen
- [ ] fix width of button text: when resize sometimes cuts off the right hand side
- [ ] fix position of time:  when resize sometimes cuts off the right hand side
  
# possibility for editing eventCells
- either all of the same title or just single one
  - edit all by iterating over whole dataset and replacing each probs
  - background color
  - name/time/etc