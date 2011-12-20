# -*- coding: utf-8 -*-
import os
import sys
import time
import threading

import sublime
import sublime_plugin

from sublimelinter.loader import Loader
from sublimelinter.modules.base_linter import INPUT_METHOD_FILE

LINTERS = {}     # mapping of language name to linter module
QUEUE = {}       # views waiting to be processed by linter
ERRORS = {}      # error messages on given line obtained from linter; they are
                 # displayed in the status bar when cursor is on line with error
VIOLATIONS = {}  # violation messages, they are displayed in the status bar
WARNINGS = {}    # warning messages, they are displayed in the status bar
TIMES = {}       # collects how long it took the linting to complete
MOD_LOAD = Loader(os.getcwd(), LINTERS)  # utility to load (and reload
                 # if necessary) linter modules [useful when working on plugin]

# For snappier linting, different delays are used for different linting times:
# (linting time, delays)
DELAYS = (
    (50, (50, 100)),
    (100, (100, 300)),
    (200, (200, 500)),
    (400, (400, 1000)),
    (800, (800, 2000)),
    (1600, (1600, 3000)),
)

MARKS = {
    "violation": ("", "dot"),
    "warning": ("", "dot"),
    "illegal": ("", "circle"),
}


def get_delay(t, view):
    delay = 0
    for _t, d in DELAYS:
        if _t <= t:
            delay = d
    delay = delay or DELAYS[0][1]

    # If the user specifies a delay greater than the built in delay,
    # figure they only want to see marks when idle.
    minDelay = int(view.settings().get('sublimelinter_delay', 0) * 1000)
    if minDelay > delay[1]:
        erase_lint_marks(view)

    return (minDelay, minDelay) if minDelay > delay[1] else delay


def last_selected_lineno(view):
    return view.rowcol(view.sel()[0].end())[0]


def update_statusbar(view):
    vid = view.id()
    lineno = last_selected_lineno(view)

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
    if linter:
        run_once(linter, view)

    if view.settings().get('sublimelinter_notes'):
        highlight_notes(view)


def run_once(linter, view):
    '''run a linter on a given view regardless of user setting'''
    if linter == LINTERS.get('annotations', None):
        highlight_notes(view)
        return

    vid = view.id()
    start = time.time()
    text = view.substr(sublime.Region(0, view.size())).encode('utf-8')
    lines, error_underlines, violation_underlines, warning_underlines, ERRORS[vid], VIOLATIONS[vid], WARNINGS[vid] = linter.run(view, text, view.file_name() or '')
    add_lint_marks(view, lines, error_underlines, violation_underlines, warning_underlines)
    update_statusbar(view)
    end = time.time()
    TIMES[vid] = (end - start) * 1000  # Keep how long it took to lint


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
        fill_outlines = view.settings().get('sublimelinter_fill_outlines', False)
        gutter_mark_enabled = True if view.settings().get('sublimelinter_gutter_marks', False) else False

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
                    'sublimelinter.{0}'.format(lint_type),
                    MARKS[lint_type][gutter_mark_enabled]
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


def get_lint_regions(view):
    regions = view.get_regions('lint-outlines-illegal')
    regions.extend(view.get_regions('lint-outlines-violation'))
    regions.extend(view.get_regions('lint-outlines-warning'))
    return regions


def select_lint_region(view, region):
    selected = view.sel()
    selected.clear()

    # Find the first underline region within the region to select.
    # If there are none, put the cursor at the beginning of the line.
    underlineRegion = find_underline_within(view, region)

    if underlineRegion is None:
        underlineRegion = sublime.Region(region.begin(), region.begin())

    selected.add(underlineRegion)
    view.show(underlineRegion, True)


def find_underline_within(view, region):
    underlines = view.get_regions('lint-underline-illegal')
    underlines.extend(view.get_regions('lint-underline-violation'))
    underlines.extend(view.get_regions('lint-underline-warning'))
    underlines.sort(key=lambda x: x.a)

    for underline in underlines:
        if region.contains(underline):
            return underline

    return None


def syntax_name(view):
    syntax = os.path.basename(view.settings().get('syntax'))
    syntax = os.path.splitext(syntax)[0]
    return syntax


def select_linter(view, ignore_disabled=False):
    '''selects the appropriate linter to use based on language in current view'''
    syntax = syntax_name(view)
    lc_syntax = syntax.lower()
    language = None
    linter = None

    if lc_syntax in LINTERS:
        language = lc_syntax
    else:
        syntaxMap = view.settings().get('sublimelinter_syntax_map', {})

        if syntax in syntaxMap:
            language = syntaxMap[syntax]

    if language:
        if ignore_disabled:
            disabled = []
        else:
            disabled = view.settings().get('sublimelinter_disable', [])

        if language not in disabled:
            linter = LINTERS[language]

            # If the enabled state is False, it must be checked.
            # Enabled checking has to be deferred to first view use because
            # user settings cannot be loaded during plugin startup.
            if not linter.enabled:
                enabled, message = linter.check_enabled(view)
                print 'SublimeLinter: {0} {1} ({2})'.format(language, 'enabled' if enabled else 'disabled', message)

                if not enabled:
                    del LINTERS[language]
                    linter = None

    return linter


def highlight_notes(view):
    '''highlight user-specified annotations in a file'''
    view.erase_regions('lint-annotations')
    text = view.substr(sublime.Region(0, view.size()))
    regions = LINTERS['annotations'].built_in_check(view, text, '')

    if regions:
        view.add_regions('lint-annotations', regions, 'sublimelinter.annotations', sublime.DRAW_EMPTY_AS_OVERWRITE)


def queue_linter(linter, view, timeout, busy_timeout, preemptive=False):
    '''Put the current view in a queue to be examined by a linter'''
    if linter is None:
        erase_lint_marks(view)  # may have changed file type and left marks behind

        # No point in queuing anything if no linters will run
        if not view.settings().get('sublimelinter_notes'):
            return

    # user annotations could be present in all types of files
    def _update_view(view):
        linter = select_linter(view)
        try:
            background_run(linter, view)
        except RuntimeError, ex:
            print ex

    queue(view, _update_view, timeout, busy_timeout, preemptive)


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
queue_thread_name = 'background linter'
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


def view_in_tab(view, title, text, file_type):
    '''Helper function to display information in a tab.
    '''
    tab = view.window().new_file()
    tab.set_name(title)
    _id = tab.buffer_id()
    tab.set_scratch(_id)
    tab.settings().set('gutter', True)
    tab.settings().set('line_numbers', False)
    tab.set_syntax_file(file_type)
    ed = tab.begin_edit()
    tab.insert(ed, 0, text)
    tab.end_edit(ed)
    return tab, _id


def lint_views(linter):
    if not linter:
        return

    viewsToLint = []

    for window in sublime.windows():
        for view in window.views():
            viewLinter = select_linter(view)

            if viewLinter == linter:
                viewsToLint.append(view)

    for view in viewsToLint:
        queue_linter(linter, view, 0, 0, True)


def reload_view_module(view):
    for name, linter in LINTERS.items():
        module = sys.modules[linter.__module__]

        if module.__file__ == view.file_name():
            print 'SublimeLinter: reloading language:', linter.language
            MOD_LOAD.reload_module(module)
            lint_views(linter)
            break


class LintCommand(sublime_plugin.TextCommand):
    '''command to interact with linters'''

    def __init__(self, view):
        self.view = view
        self.help_called = False

    def run_(self, action):
        '''method called by default via view.run_command;
           used to dispatch to appropriate method'''
        if not action:
            return

        try:
            lc_action = action.lower()
        except AttributeError:
            return

        if lc_action == 'reset':
            self.reset()
        elif lc_action == 'on':
            self.on()
        elif lc_action == 'load-save':
            self.enable_load_save()
        elif lc_action == 'off':
            self.off()
        elif action.lower() in LINTERS:
            self._run(lc_action)

    def reset(self):
        '''Removes existing lint marks and restores user settings.'''
        erase_lint_marks(self.view)
        settings = sublime.load_settings('Base File.sublime-settings')
        self.view.settings().set('sublimelinter', settings.get('sublimelinter', True))

    def on(self):
        '''Turns background linting on.'''
        self.view.settings().set('sublimelinter', True)
        queue_linter(select_linter(self.view), self.view, 0, 0, True)

    def enable_load_save(self):
        '''Turns load-save linting on.'''
        self.view.settings().set('sublimelinter', 'load-save')
        print self.view.settings().get('sublimelinter')
        erase_lint_marks(self.view)

    def off(self):
        '''Turns background linting off.'''
        self.view.settings().set('sublimelinter', False)
        erase_lint_marks(self.view)

    def _run(self, name):
        '''runs an existing linter'''
        self.view.settings().set('sublimelinter', False)
        run_once(LINTERS[name.lower()], self.view)


class BackgroundLinter(sublime_plugin.EventListener):
    '''This plugin controls a linter meant to work in the background
    to provide interactive feedback as a file is edited. It can be
    turned off via a setting.
    '''

    def __init__(self):
        super(BackgroundLinter, self).__init__()
        self.lastSelectedLineNo = -1

    def on_modified(self, view):
        if view.is_scratch():
            return

        if view.settings().get('sublimelinter') != True:
            erase_lint_marks(view)
            return

        linter = select_linter(view)

        # File-based linters are not invoked during a modify
        if linter and linter.input_method == INPUT_METHOD_FILE:
            erase_lint_marks(view)
            return

        delay = get_delay(TIMES.get(view.id(), 100), view)
        queue_linter(linter, view, *delay)

    def on_load(self, view):
        if view.is_scratch() or view.settings().get('sublimelinter') == False:
            return
        background_run(select_linter(view), view)

    def on_post_save(self, view):
        if view.is_scratch() or view.settings().get('sublimelinter') == False:
            return

        reload_view_module(view)
        background_run(select_linter(view), view)

    def on_selection_modified(self, view):
        if view.is_scratch():
            return
        delay_queue(1000)  # on movement, delay queue (to make movement responsive)

        # We only display errors in the status bar for the last line in the current selection.
        # If that line number has not changed, there is no point in updating the status bar.
        lastSelectedLineNo = last_selected_lineno(view)

        if lastSelectedLineNo != self.lastSelectedLineNo:
            self.lastSelectedLineNo = lastSelectedLineNo
            update_statusbar(view)


class FindLintErrorCommand(sublime_plugin.TextCommand):
    '''This command is just a superclass for other commands, it is never enabled.'''
    def is_enabled(self):
        return select_linter(self.view) is not None

    def find_lint_error(self, forward):
        regions = get_lint_regions(self.view)

        if len(regions) == 0:
            sublime.error_message('No lint errors.')
            return

        selected = self.view.sel()
        point = selected[0].begin() if forward else selected[-1].end()
        regionToSelect = None

        # If going forward, find the first region beginning after the point.
        # If going backward, find the first region ending before the point.
        # If nothing is found in the given direction, wrap to the first/last region.
        if forward:
            regions.sort(key=lambda x: x.a)

            for index, region in enumerate(regions):
                if point < region.begin():
                    regionToSelect = region
                    break
        else:
            regions.sort(key=lambda x: x.a, reverse=True)

            for index, region in enumerate(regions):
                if point > region.end():
                    regionToSelect = region
                    break

        # If there is only one error line and the cursor is in that line, we cannot move.
        # Otherwise wrap to the first/last error line unless settings disallow that.
        if regionToSelect is None and (len(regions) > 1 or not regions[0].contains(point)):
            if self.view.settings().get('sublimelinter_wrap_find', True):
                regionToSelect = regions[0]

        if regionToSelect is not None:
            select_lint_region(self.view, regionToSelect)
        else:
            sublime.error_message('No {0} lint errors.'.format('next' if forward else 'previous'))


class FindNextLintErrorCommand(FindLintErrorCommand):
    def run(self, edit):
        '''
        Move the cursor to the next lint error in the current view.
        The search will wrap to the top unless the sublimelinter_wrap_find
        setting is set to false.
        '''
        self.find_lint_error(forward=True)


class FindPreviousLintErrorCommand(FindLintErrorCommand):
    def run(self, edit):
        '''
        Move the cursor to the previous lint error in the current view.
        The search will wrap to the bottom unless the sublimelinter_wrap_find
        setting is set to false.
        '''
        self.find_lint_error(forward=False)


class SublimelinterWindowCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        view = self.window.active_view()

        if view:
            if view.is_scratch():
                return False
            else:
                return True
        else:
            return False

    def run_(self, args):
        pass


class SublimelinterAnnotationsCommand(SublimelinterWindowCommand):
    '''Commands to extract annotations and display them in
       a file
    '''
    def run_(self, args):
        linter = LINTERS.get('annotations', None)

        if linter is None:
            return

        view = self.window.active_view()

        if not view:
            return

        text = view.substr(sublime.Region(0, view.size()))
        filename = view.file_name()
        notes = linter.extract_annotations(text, view, filename)
        _, filename = os.path.split(filename)
        annotations_view, _id = view_in_tab(view, 'Annotations from %s' % filename, notes, '')


class SublimelinterCommand(SublimelinterWindowCommand):
    def is_enabled(self):
        enabled = super(SublimelinterCommand, self).is_enabled()

        if not enabled:
            return False

        linter = select_linter(self.window.active_view(), ignore_disabled=True)
        return linter is not None

    def run_(self, args={}):
        view = self.window.active_view()
        action = args.get('action', '')

        if view and action:
            if action == 'lint':
                self.lint_view(view)
            else:
                view.run_command('lint', action)

    def lint_view(self, view):
        linter = select_linter(view, ignore_disabled=True)

        if linter:
            view.run_command('lint', linter.language)
            regions = get_lint_regions(view)

            if regions:
                sublime.error_message('{0} lint error{1}.'.format(len(regions), 's' if len(regions) != 1 else ''))
            else:
                sublime.error_message('No lint errors.')
        else:
            syntax = syntax_name(view)
            sublime.error_message('No linter for the syntax "{0}"'.format(syntax))


class SublimelinterLintCommand(SublimelinterCommand):
    def is_enabled(self):
        enabled = super(SublimelinterLintCommand, self).is_enabled()

        if enabled:
            view = self.window.active_view()

            if view and view.settings().get('sublimelinter') == True:
                return False

        return enabled


class SublimelinterEnableLoadSaveCommand(SublimelinterCommand):
    def is_enabled(self):
        enabled = super(SublimelinterEnableLoadSaveCommand, self).is_enabled()

        if enabled:
            view = self.window.active_view()

            if view and view.settings().get('sublimelinter') == 'load-save':
                return False

        return enabled


class SublimelinterDisableCommand(SublimelinterCommand):
    def is_enabled(self):
        enabled = super(SublimelinterDisableCommand, self).is_enabled()

        if enabled:
            view = self.window.active_view()

            if view and not view.settings().get('sublimelinter') == True:
                return False

        return enabled
