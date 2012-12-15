countdown
=========

Countdown reads a config file and shows the days/months/years until/past each
event

Example output:

    -- Default Group ---------------------------------
       349 days ago  - New Year's Day
        11 days left - Christmas

Countdown reads $HOME/.countdownrc (or other if specified on the command line)
and parses events from it. Dates are specified in YYYY-mm-dd format. If a date
ends in !, it includes both end days, otherwise, it only includes one. Blank
lines and lines starting with # are ignored. Sections can be created by making
the first char -.

Example config file:

    - Section Title
    YYYY-mm-dd[!] [event description]


