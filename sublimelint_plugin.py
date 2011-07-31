'''This plugin controls a linter meant to work in the background
and to provide information as a file is edited.

It requires that the user setting "sublimelint" be set to true
to be activated - or, alternatively, that the user runs the command
view.run_command("lint", "on")

Questions: andre.roberge (at) gmail.com
'''
import os
import time
import threading

import sublime
import sublime_plugin

from sublimelint.loader import Loader

LINTERS = {}     # mapping of language name to linter module
QUEUE = {}       # views waiting to be processed by linter
ERRORS = {}      # error messages on given line obtained from linter; they are
                 # displayed in the status bar when cursor is on line with error
VIOLATIONS = {}  # violation messages, they are displayed in the status bar
WARNINGS = {}    # warning messages, they are displayed in the status bar
HELP = []        # collects all "help" (docstring, etc.) information
MOD_LOAD = Loader(os.getcwd(), LINTERS, HELP)  # utility to load (and reload
                 # if necessary) linter modules [useful when working on plugin]

HELP.insert(0,
'''SublimeLint help
=================

SublimeLint is a plugin intended to support "lint" programs, highlighting
lines of code which are deemed to contain (potential) errors. It also
supports highlighting special annotations (for example: TODO) so that they
can be quickly located.

To enable a background linter to run by default
(provided one exists for the language/syntax the file being viewed), set
the user preference "sublimelint" to true.   If you find that this slows
down the UI too much, you can unset this user preference (or set it to
false) and use the special commands (described below) to run it only
on demand.

When an "error" is highlighted by the linter, putting the cursor on the
offending line will result in the error message being displayed on the
status bar.


Color: lint "errors"
--------------------

There are three types of "errors" flagged by sublime lint: illegal,
violation, and warning. For each type, SublimeLint will indicate the offending
line and the character position at which the error occurred on the line.

By default SublimeLint will outline offending lines using the background color
of the "sublimelint.<type>" theme style, and underline the character position
using the background color of the "invalid.<type>" theme style, where <type>
is one of the three error types.

If these styles are not defined, the color will be black when there is a light
background color and black when there is a dark background color. You may
define a single "sublimelint" or "invalid" style to color all three types,
or define separate substyles for one or more types to color them differently.
Most themes have an "invalid" theme style defined by default.

If you want to make the offending lines glaringly obvious (perhaps for those
who tend to ignore lint errors), you can set the user setting "sublimelint_fill_outlines"
to true, in which case lines that have errors will be colored with the background
and foreground color of the "sublime.<type>" theme style. Unless you have defined
those styles, this setting should be left false.

To customize the colors used for highlighting errors and user notes, add the following
to your theme (adapting the color to your liking):
        <dict>
            <key>name</key>
            <string>Sublimelint Annotations</string>
            <key>scope</key>
            <string>sublimelint.notes</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FFFFAA</string>
                <key>foreground</key>
                <string>#FFFFFF</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Sublimelint Outline</string>
            <key>scope</key>
            <string>sublimelint.illegal</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FF4A52</string>
                <key>foreground</key>
                <string>#FFFFFF</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Sublimelint Underline</string>
            <key>scope</key>
            <string>invalid.illegal</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FF0000</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Sublimelint Warning Outline</string>
            <key>scope</key>
            <string>sublimelint.warning</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#DF9400</string>
                <key>foreground</key>
                <string>#FFFFFF</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Sublimelint Warning Underline</string>
            <key>scope</key>
            <string>invalid.warning</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FF0000</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Sublimelint Violation Outline</string>
            <key>scope</key>
            <string>sublimelint.violation</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#ffffff33</string>
                <key>foreground</key>
                <string>#FFFFFF</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Sublimelint Violation Underline</string>
            <key>scope</key>
            <string>invalid.violation</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>#FF0000</string>
            </dict>
        </dict>

==================================================================

The following information is extracted dynamically from the source
code files and *should* be reflecting accurately all the available
options:
------------------------------------------------------------------
'''
)


def help_collector(fn):
    '''decorator used to automatically extract docstrings and collect them
    for future display'''
    HELP.append(fn.__doc__)
    return fn


def update_statusbar(view):
    vid = view.id()
    lineno = view.rowcol(view.sel()[0].end())[0]

    if vid in ERRORS and lineno in ERRORS[vid]:
        view.set_status('Linter', '; '.join(ERRORS[vid][lineno]))
    elif vid in VIOLATIONS and lineno in VIOLATIONS[vid]:
        view.set_status('Linter', '; '.join(VIOLATIONS[vid][lineno]))
    elif vid in WARNINGS and lineno in WARNINGS[vid]:
        view.set_status('Linter', '; '.join(WARNINGS[vid][lineno]))
    else:
        view.erase_status('Linter')


def background_run(linter, view):
    '''run a linter on a given view if settings is set appropriately'''
    if view.settings().get('sublimelint'):
        if linter:
            run_once(linter, view)
    if view.settings().get('sublimelint_notes'):
        highlight_notes(view)


def run_once(linter, view):
    '''run a linter on a given view regardless of user setting'''
    if linter == LINTERS["annotations"]:
        highlight_notes(view)
        return
    vid = view.id()
    text = view.substr(sublime.Region(0, view.size())).encode('utf-8')
    if view.file_name():
        filename = view.file_name()  # os.path.split(view.file_name())[-1]
    else:
        filename = 'untitled'
    lines, error_underlines, violation_underlines, warning_underlines, ERRORS[vid], VIOLATIONS[vid], WARNINGS[vid] = linter.run(text, view, filename)
    add_lint_marks(view, lines, error_underlines, violation_underlines, warning_underlines)
    update_statusbar(view)


def add_lint_marks(view, lines, error_underlines, violation_underlines, warning_underlines):
    '''Adds lint marks to view.'''
    vid = view.id()
    erase_lint_marks(view)
    if warning_underlines:
        view.add_regions('lint-underline-warning', warning_underlines, 'invalid.warning', sublime.DRAW_EMPTY_AS_OVERWRITE)
    if violation_underlines:
        view.add_regions('lint-underline-violation', violation_underlines, 'invalid.violation', sublime.DRAW_EMPTY_AS_OVERWRITE)
    if error_underlines:
        view.add_regions('lint-underline-illegal', error_underlines, 'invalid.illegal', sublime.DRAW_EMPTY_AS_OVERWRITE)
    if lines:
        fill_outlines = view.settings().get('sublimelint_fill_outlines', False)
        outlines = {'warning': [], 'violation': [], 'illegal': []}
        for line in lines:
            if line in ERRORS[vid]:
                outlines['illegal'].append(view.full_line(view.text_point(line, 0)))
            elif line in WARNINGS[vid]:
                outlines['warning'].append(view.full_line(view.text_point(line, 0)))
            elif line in VIOLATIONS[vid]:
                outlines['violation'].append(view.full_line(view.text_point(line, 0)))
        for lint_type in outlines:
            if outlines[lint_type]:
                args = [
                    'lint-outlines-{0}'.format(lint_type),
                    outlines[lint_type],
                    'sublimelint.{0}'.format(lint_type),
                    'cross'
                ]
                if not fill_outlines:
                    args.append(sublime.DRAW_OUTLINED)
                view.add_regions(*args)


def erase_lint_marks(view):
    '''erase all "lint" error marks from view'''
    view.erase_regions('lint-underline-illegal')
    view.erase_regions('lint-underline-violation')
    view.erase_regions('lint-underline-warning')
    view.erase_regions('lint-outlines-illegal')
    view.erase_regions('lint-outlines-violation')
    view.erase_regions('lint-outlines-warning')


def select_linter(view):
    '''selects the appropriate linter to use based on language in
       current view'''
    for language in LINTERS:
        if language in view.settings().get("syntax"):
            return LINTERS[language]
    return None


def highlight_notes(view):
    '''highlight user-specified annotations in a file'''
    view.erase_regions('lint-annotations')
    text = view.substr(sublime.Region(0, view.size()))
    regions = LINTERS["annotations"].run(text, view)
    if regions:
        view.add_regions('lint-annotations', regions, "sublimelint.annotations", sublime.DRAW_EMPTY_AS_OVERWRITE)


def queue_linter(view):
    '''Put the current view in a queue to be examined by a linter'''
    if select_linter(view) is None:
        erase_lint_marks(view)  # may have changed file type and left marks behind

    # user annotations could be present in all types of files
    def _update_view(view):
        linter = select_linter(view)
        try:
            background_run(linter, view)
        except RuntimeError, excp:
            print excp
    queue(view, _update_view, 400, 1000)


def background_linter():
    __lock_.acquire()
    try:
        views = QUEUE.values()
        QUEUE.clear()
    finally:
        __lock_.release()
    for view, callback, args, kwargs in views:
        def _callback():
            callback(view, *args, **kwargs)
        sublime.set_timeout(_callback, 0)

################################################################################
# Queue dispatcher system:

queue_dispatcher = background_linter
queue_thread_name = "background linter"
MAX_DELAY = 10


def queue_loop():
    '''An infinite loop running the linter in a background thread meant to
        update the view after user modifies it and then does no further
        modifications for some time as to not slow down the UI with linting.'''
    global __signaled_, __signaled_first_
    while __loop_:
        #print 'acquire...'
        __semaphore_.acquire()
        __signaled_first_ = 0
        __signaled_ = 0
        #print 'DISPATCHING!', len(QUEUE)
        queue_dispatcher()


def queue(view, callback, timeout, busy_timeout=None, preemptive=False, args=[], kwargs={}):
    global __signaled_, __signaled_first_
    now = time.time()
    __lock_.acquire()
    try:
        QUEUE[view.id()] = (view, callback, args, kwargs)
        if now < __signaled_ + timeout * 4:
            timeout = busy_timeout or timeout

        __signaled_ = now
        _delay_queue(timeout, preemptive)
        if not __signaled_first_:
            __signaled_first_ = __signaled_
            #print 'first',
        #print 'queued in', (__signaled_ - now)
    finally:
        __lock_.release()


def _delay_queue(timeout, preemptive):
    global __signaled_, __queued_
    now = time.time()
    if not preemptive and now <= __queued_ + 0.01:
        return  # never delay queues too fast (except preemptively)
    __queued_ = now
    _timeout = float(timeout) / 1000
    if __signaled_first_:
        if MAX_DELAY > 0 and now - __signaled_first_ + _timeout > MAX_DELAY:
            _timeout -= now - __signaled_first_
            if _timeout < 0:
                _timeout = 0
            timeout = int(round(_timeout * 1000, 0))
    new__signaled_ = now + _timeout - 0.01
    if __signaled_ >= now - 0.01 and (preemptive or new__signaled_ >= __signaled_ - 0.01):
        __signaled_ = new__signaled_
        #print 'delayed to', (preemptive, __signaled_ - now)

        def _signal():
            if time.time() < __signaled_:
                return
            __semaphore_.release()
        sublime.set_timeout(_signal, timeout)


def delay_queue(timeout):
    __lock_.acquire()
    try:
        _delay_queue(timeout, False)
    finally:
        __lock_.release()


# only start the thread once - otherwise the plugin will get laggy
# when saving it often.
__semaphore_ = threading.Semaphore(0)
__lock_ = threading.Lock()
__queued_ = 0
__signaled_ = 0
__signaled_first_ = 0

# First finalize old standing threads:
__loop_ = False
__pre_initialized_ = False


def queue_finalize(timeout=None):
    global __pre_initialized_
    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == queue_thread_name:
            __pre_initialized_ = True
            thread.__semaphore_.release()
            thread.join(timeout)
queue_finalize()

# Initialize background thread:
__loop_ = True
__active_linter_thread = threading.Thread(target=queue_loop, name=queue_thread_name)
__active_linter_thread.__semaphore_ = __semaphore_
__active_linter_thread.start()

################################################################################

UNRECOGNIZED = '''
* Unrecognized option * :  %s
==============================================

'''


class Lint(sublime_plugin.TextCommand):
    '''command to interact with linters'''

    def __init__(self, view):
        self.view = view
        self.help_called = False

    def run_(self, name):
        '''method called by default via view.run_command;
           used to dispatch to appropriate method'''
        if name is None:
            self.help_()
            return

        try:
            lc_name = name.lower()
        except AttributeError:
            HELP.insert(0, UNRECOGNIZED % name)
            self.help()
            del HELP[0]
            return

        if lc_name == "help":
            self.help()
        elif lc_name == "reset":
            self.reset()
        elif lc_name == "on":
            self.on()
        elif lc_name == "off":
            self.off()
        elif name in LINTERS:
            self._run(name)
        else:
            HELP.insert(0, UNRECOGNIZED % name)
            self.help()
            del HELP[0]

    @help_collector
    def help_(self):
        '''* view.run_command("lint"):
        Displays information about how to use this plugin
        '''
        self.help()

    @help_collector
    def help(self):
        '''* view.run_command("lint", "help"):
        Displays information about how to use this plugin
        '''
        help_view, _id = self.view_in_tab("Sublime help", '\n'.join(HELP),
                                    "Packages/Markdown/Markdown.tmLanguage")
        help_view.set_read_only(_id)

    def view_in_tab(self, title, text, file_type):
        '''Helper function to display information in a tab.
        '''
        tab = self.view.window().new_file()
        tab.set_name(title)
        _id = tab.buffer_id()
        tab.set_scratch(_id)
        tab.settings().set("gutter", True)
        tab.settings().set("line_numbers", False)
        tab.set_syntax_file(file_type)
        ed = tab.begin_edit()
        tab.insert(ed, 0, text)
        tab.end_edit(ed)
        return tab, _id

    @help_collector
    def reset(self):
        '''* view.run_command("lint", "reset")
        Removes existing lint marks and restore (if needed) the settings
        so that the relevant "background" linter can run.
        '''
        erase_lint_marks(self.view)
        if self.view.settings().get('sublimelint') is None:
            self.view.settings().set('sublimelint', True)

    @help_collector
    def on(self):
        '''* view.run_command("lint", "on")
        Turns background linter on.
        '''
        self.view.settings().set('sublimelint', True)

    @help_collector
    def off(self):
        '''* view.run_command("lint", "off")
        Turns background linter off.
        '''
        self.view.settings().set('sublimelint', False)

    def _run(self, name):
        '''runs an existing linter'''
        if self.view.settings().get('sublimelint'):
            self.view.settings().set('sublimelint', None)
        run_once(LINTERS[name], self.view)


class Annotations(Lint):
    '''Commands to extract annotations and display them in
       a file
    '''
    def run_(self, name):
        '''method called by default via view.run_command;
           used to dispatch to appropriate method'''
        if name is None:
            self.extract_from_current_view()
            return

        try:
            lc_name = name.lower()
        except AttributeError:
            HELP.insert(0, UNRECOGNIZED % name)
            self.help()
            del HELP[0]
            return

        if lc_name == "help":
            self.help()
        else:
            HELP.insert(0, UNRECOGNIZED % name)
            self.help()
            del HELP[0]

    def extract_from_current_view(self):
        text = self.view.substr(sublime.Region(0, self.view.size()))
        filename = self.view.file_name()
        notes = LINTERS["annotations"].extract_annotations(text, self.view, filename)
        _, filename = os.path.split(filename)
        annotations_view, _id = self.view_in_tab("Annotations from %s" %
                                                    filename, notes,
                                                "Packages/sublime_orgmode/orgmode.tmLanguage")


class BackgroundLinter(sublime_plugin.EventListener):
    '''This plugin controls a linter meant to work in the background
    and to provide information as a file is edited.
    For all practical purpose, it is possible to turn it off
    via a user-defined settings.
    '''
    def on_modified(self, view):
        queue_linter(view)
        return

    def on_load(self, view):
        linter = select_linter(view)
        if linter:
            background_run(linter, view)

    def on_post_save(self, view):
        for name, module in LINTERS.items():
            if module.__file__ == view.file_name():
                print 'SublimeLint - Reloading language:', module.language
                MOD_LOAD.reload_module(module)
                break
        queue_linter(view)

    def on_selection_modified(self, view):
        delay_queue(1000)  # on movement, delay queue (to make movement responsive)
        update_statusbar(view)
