# small/random stuff
- [ ] may need extra ical packages: https://icalendar.readthedocs.io/en/stable/#related-projects
- [ ] make links in description clickable: https://textual.textualize.io/widgets/link/#__tabbed_1_2
- [ ] make css reactive
- [ ] account for multi-day events
- [ ] how to properly add venv to git?
- [ ] set font size on start
- [ ] split up css
- [ ] in EventScreen, the grid-rows parameter is still wonky giving Labels more padding/margins than they need. Bug?

# command line args

# next/prev week
- [ ] add way to write desired week into command?

# alignment
- [ ] account for multi-day events
- [ ] make resolution more modular/editable by user?
- [ ] events displayed off by 15 sometimes?

# coloring
- [ ] depending on if light or dark color theme, edit function
- [ ] let person set color for event(s)
- [ ] set color based on calendar (all events same color)
  - [ ] two modes: calendar/default and timetable

# tests
- [ ] add unittests

# add keyboard navigation
- [ ] add vim keybinds?
- [ ] add screen that shows all key commands (already available (editable?) under palette)
- [ ] mouse button to escape from event view?

# cleanup/refactoring/restructuring
- [ ] make all variables lower_case_with_underscores instead of CapitalizedWords
- [ ] rename some variables?
- [ ] make pep8 compliant: get vscode plugin
- [ ] restructure code
- [ ] read up on import best practices

# edit/add new events
- [ ] implement a edit event in eventScreen
- [ ] does icalendar validate the data or do i need to do it? You can create custom validators
  - [ ] what type of inputtable variables exist?: see https://icalendar.readthedocs.io/en/stable/api.html under icalender.cal.Event ? i think maybe?
  - [ ] select button of which calendar(s) to add event to
  - [ ] delete event(s)
- [ ] edit either all of the same title or just single one
  - [ ] edit all by iterating over whole dataset and replacing each probs
- [ ] background color
- [ ] name/time/etc

# implement calDav

# send push notifications

# bugs:
- [ ] fix width of button text: when resize sometimes cuts off the right hand side
- [ ] erroring when writing to calendar fucks up the calendar. that is bad

# config file
- [ ] edit key binds
- [ ] edit hour resolution? (change in week_prototype.py and tcss)