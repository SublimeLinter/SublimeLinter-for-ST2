SublimeLinter
=============

SublimeLinter is a plugin that supports "lint" programs (known as "linters"). SublimeLinter highlights
lines of code the linter deems to contain (potential) errors. It also
supports highlighting special annotations (for example: TODO) so that they
can be quickly located.

SublimeLinter has built in linters for the following languages:

* Javascript - lint via built in [jshint](http://jshint.org) run by JavaScriptCore on OS X or node.js on other platforms. You must install node.js, see [the node.js site](http://nodejs.com) for instructions.
* Objective-J - lint via built-in [capp_lint](https://github.com/aparajita/capp_lint)
* python - native, moderately-complete lint
* ruby - syntax checking via "ruby -wc"
* php - syntax checking via "php -l"
* java - lint via "javac -Xlint"
* perl - syntax+deprecation checking via "perl -c"

Installing
----------
**With the Package Control plugin:** The easiest way to install SublimeLinter is through Package Control, which can be found at this site: [http://wbond.net/sublime_packages/package_control](http://wbond.net/sublime_packages/package_control)

Once you install Package Control, restart ST2 and bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select SublimeLinter when the list appears. The advantage of using this method is that Package Control will automatically keep SublimeLinter up to date with the latest version.

**Without Git:** Download the latest source from [github](http://github.com/Kronuz/SublimeLinter) and copy the SublimeLinter folder to your Sublime Text "Packages" directory.

**With Git:** Clone the repository in your Sublime Text "Packages" directory:

    git clone git://github.com/Kronuz/SublimeLinter.git

The "Packages" directory is located at:

* OS X:
    ~/Library/Application Support/Sublime Text 2/Packages/
* Linux:
    ~/.Sublime Text 2/Packages/
* Windows:
    %APPDATA%/Sublime Text 2/Packages/

Using
-----
SublimeLinter runs in one of three modes, which is determined by the "sublimelinter" user setting:

* **Background mode (the default)** - When the "sublimelinter" setting is true, linting is performed in the background as you modify a file (if the relevant linter supports it). If you like instant feedback, this is the best way to use SublimeLinter. If you want feedback, but not instantly, you can try another mode or set a minimum queue delay so that the linter will only run after a certain amount of idle time.
* **Load-save mode** - When the "sublimelinter" setting is "load-save", linting is performed only when a file is loaded and after saving. Errors are cleared as soon as the file is modified.
* **On demand mode** - When the "sublimelinter" setting is false, linting is performed only when initiated by you. Use the Control+Command+l (OS X) or Control+Alt+l (Linux/Windows) key equivalent or the Command Palette to lint the current file. If the current file has no associated linter, the command will not be available.

Within a file whose language/syntax is supported by SublimeLinter, you can control SublimeLinter via the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows). The available commands are:

* **SublimeLinter: Lint Current File** — Lints the current file, highlights any errors and displays how many errors were found. After using this command, the current view will not be linted until requested by this command or until background or load-save linting mode is enabled.
* **SublimeLinter: Enable Background Linting** — Enables background linting mode for the current view and lints it.
* **SublimeLinter: Disable Background Linting** — Disables background linting mode for the current view and clears all lint errors.
* **SublimeLinter: Enable Load-Save Linting** — Enables load-save linting mode for the current view and clears all lint errors.
* **SublimeLinter: Reset** — Clears all lint errors and sets the linting mode to the value in the Base File settings.

Depending on the file and the current state of background enabling, some of the commands will not be available.

When an error is highlighted by the linter, putting the cursor on the offending line will result in the error message being displayed on the status bar.

You can quickly move to the next/previous lint error with the following key equivalents:

**OS X**
next: Control+Command+e
prev: Control+Command+Shift+e

**Linux, Windows**
next: Control+Alt+e
prev: Control+Alt+Shift+e

By default the search will wrap. You can turn wrapping off with the user setting:

    "sublimelinter_wrap_find": false

Configuring
-----------
There are a number of configuration options available to customize the behavior of SublimeLinter and its linters. For the latest information on what options are available, select the menu item Preferences->Package Settings->SublimeLinter->Settings - Default.

### Customizing colors
There are three types of "errors" flagged by sublime lint: illegal,
violation, and warning. For each type, SublimeLinter will indicate the offending
line and the character position at which the error occurred on the line.

By default SublimeLinter will outline offending lines using the background color
of the "sublimelinter.<type>" theme style, and underline the character position
using the background color of the "invalid.<type>" theme style, where <type>
is one of the three error types.

If these styles are not defined, the color will be black when there is a light
background color and black when there is a dark background color. You may
define a single "sublimelinter" or "invalid" style to color all three types,
or define separate substyles for one or more types to color them differently.
Most themes have an "invalid" theme style defined by default.

If you want to make the offending lines glaringly obvious (perhaps for those
who tend to ignore lint errors), you can set the user setting:

    "sublimelinter_fill_outlines": true

When this is set true, lines that have errors will be colored with the background
and foreground color of the "sublime.<type>" theme style. Unless you have defined
those styles, this setting should be left false.

You may also mark lines with errors by putting an "x" in the gutter with the user setting:

    "sublimelinter_gutter_marks": true

To customize the colors used for highlighting errors and user notes, add the following
to your theme (adapting the color to your liking):

    <dict>
        <key>name</key>
        <string>SublimeLinter Annotations</string>
        <key>scope</key>
        <string>sublimelinter.notes</string>
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
        <string>SublimeLinter Outline</string>
        <key>scope</key>
        <string>sublimelinter.illegal</string>
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
        <string>SublimeLinter Underline</string>
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
        <string>SublimeLinter Warning Outline</string>
        <key>scope</key>
        <string>sublimelinter.warning</string>
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
        <string>SublimeLinter Warning Underline</string>
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
        <string>SublimeLinter Violation Outline</string>
        <key>scope</key>
        <string>sublimelinter.violation</string>
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
        <string>SublimeLinter Violation Underline</string>
        <key>scope</key>
        <string>invalid.violation</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#FF0000</string>
        </dict>
    </dict>

Troubleshooting
---------------
If a linter does not seem to be working, you can check the ST2 console to see if it was enabled. When SublimeLinter is loaded, you will see messages in the console like this:

    Reloading plugin /Users/aparajita/Library/Application Support/Sublime Text 2/Packages/SublimeLinter/sublimelinter_plugin.py
    SublimeLinter: JavaScript loaded
    SublimeLinter: annotations loaded
    SublimeLinter: Objective-J loaded
    SublimeLinter: perl loaded
    SublimeLinter: php loaded
    SublimeLinter: python loaded
    SublimeLinter: ruby loaded
    SublimeLinter: pylint loaded

The first time a linter is asked to lint, it will check to see if it can be enabled. You will then see messages like this:

    SublimeLinter: JavaScript enabled (using JavaScriptCore)
    SublimeLinter: Ruby enabled (using "ruby" for executable)

Let's say the ruby linter is not working. If you look at the console, you may see a message like this:

    SublimeLinter: ruby disabled ("ruby" cannot be found)

This means that the ruby executable cannot be found on your system, which means it is not installed or not in your executable path.

Creating New Linters
--------------------
If you wish to create a new linter to support a new language, SublimeLinter makes it easy. Here are the steps involved:

* Create a new file in sublimelinter/modules. If your linter uses an external executable, you will probably want to copy perl.py. If your linter uses built in code, copy objective-j.py. The convention is to name the file the same as the language that will be linted.

* Configure the CONFIG dict in your module. See the comments in base\_linter.py for information on the values in that dict. You only need to set the values in your module that differ from the defaults in base\_linter.py, as your module's CONFIG is merged with the default. Note that if your linter uses an external executable that does not take stdin, setting 'input\_method' to INPUT\_METHOD\_TEMP\_FILE will allow interactive linting with that executable.

* If your linter uses built in code, override `built_in_check()` and return the errors found.

* Override `parse_errors()` and process the errors. If your linter overrides `built_in_check()`, `parse_errors()` will receive the result of that method. If your linter uses an external executable, `parse_errors()` receives the raw output of the executable, stripped of leading and trailing whitespace.

If your linter has more complex requirements, see the comments for CONFIG in base\_linter.py, and use the existing linters as guides.
