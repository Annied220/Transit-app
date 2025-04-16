This is the transit Application for finding bus time stops in any location in the state of Connecticut.

The API key is distributed privately among developers, you may also provide your own if you wish to build this application yourself.

Built using graphics libraries in Python and external APIs for data retreival.

Does not have resizeable UI yet, DO NOT PUSH DANGEROUS OR HUGE CHANGES TO MAIN, check with everyone else first.

ISSUES WHICH NEED TO BE FIXED WITH RESIZEABLE WINDOW CHANGE:
Placeholder text in the search entry is causing the UI elements to noticably shift slightly, while this is most likely an issue with offsets with our hacky method of implemting the placeholder text
at all, it is something which should be looked into.

THINGS TO CONSIDER:
The API key has a limited number of requests we can use for free. We should be consertative when it comes to testing the search function as it calls the API twice instead of once. Do not want to end up needing
to pay for the API if we run out of requests.
