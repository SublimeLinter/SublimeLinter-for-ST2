SublimeLinter
=============

SublimeLinter is a plugin that supports "lint" programs (known as "linters"). SublimeLinter highlights
lines of code the linter deems to contain (potential) errors. It also
supports highlighting special annotations (for example: TODO) so that they
can be quickly located.

SublimeLinter has built in linters for the following languages:

* Javascript - lint via built in `jshint <http://jshint.org>`_
* Objective-J - lint via built-in `capp_lint <https://github.com/aparajita/capp_lint>`_
* python - native, moderately-complete lint
* ruby - syntax checking via "ruby -wc"
* php - syntax checking via "php -l"
* java - lint via "javac -Xlint"
* perl - syntax+deprecation checking via "perl -c"

.. image:: http://pledgie.com/campaigns/16512.png?skin_name=chrome
   :alt: Click here to lend your support to SublimeLinter and make a donation at pledgie.com!
   :target: http://pledgie.com/campaigns/16512


Installing
----------
**With the Package Control plugin:** The easiest way to install SublimeLinter is through Package Control, which can be found at this site: http://wbond.net/sublime_packages/package_control

Once you install Package Control, restart ST2 and bring up the Command Palette (``Command+Shift+P`` on OS X, ``Control+Shift+P`` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select SublimeLinter when the list appears. The advantage of using this method is that Package Control will automatically keep SublimeLinter up to date with the latest version.

**Without Git:** Download the latest source from `GitHub <http://github.com/Kronuz/SublimeLinter>`_ and copy the SublimeLinter folder to your Sublime Text "Packages" directory.

**With Git:** Clone the repository in your Sublime Text "Packages" directory::

    git clone git://github.com/Kronuz/SublimeLinter.git


The "Packages" directory is located at:

* OS X::

    ~/Library/Application Support/Sublime Text 2/Packages/

* Linux::

    ~/.config/sublime-text-2/Packages/

* Windows::

    %APPDATA%/Sublime Text 2/Packages/

Using
-----
SublimeLinter runs in one of three modes, which is determined by the "sublimelinter" user setting:

* **Background mode (the default)** - When the "sublimelinter" setting is true, linting is performed in the background as you modify a file (if the relevant linter supports it). If you like instant feedback, this is the best way to use SublimeLinter. If you want feedback, but not instantly, you can try another mode or set a minimum queue delay so that the linter will only run after a certain amount of idle time.
* **Load-save mode** - When the "sublimelinter" setting is "load-save", linting is performed only when a file is loaded and after saving. Errors are cleared as soon as the file is modified.
* **On demand mode** - When the "sublimelinter" setting is false, linting is performed only when initiated by you. Use the Control+Command+l (OS X) or Control+Alt+l (Linux/Windows) key equivalent or the Command Palette to lint the current file. If the current file has no associated linter, the command will not be available.

Within a file whose language/syntax is supported by SublimeLinter, you can control SublimeLinter via the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows). The available commands are:

* **SublimeLinter: Lint Current File** — Lints the current file, highlights any errors and displays how many errors were found.
* **SublimeLinter: Show Error List** — Lints the current file, highlights any errors and displays a quick panel with any errors that are found. Selecting an item from the quick panel jumps to that line.
* **SublimeLinter: Enable Background Linting** — Enables background linting mode for the current view and lints it.
* **SublimeLinter: Disable Background Linting** — Disables background linting mode for the current view and clears all lint errors.
* **SublimeLinter: Enable Load-Save Linting** — Enables load-save linting mode for the current view and clears all lint errors.
* **SublimeLinter: Reset** — Clears all lint errors and sets the linting mode to the value in the Base File settings.

Depending on the file and the current state of background enabling, some of the commands will not be available.

When an error is highlighted by the linter, putting the cursor on the offending line will result in the error message being displayed on the status bar.

If you want to be shown a popup list of all errors whenever a file is saved, modify the user setting::

    "sublimelinter_popup_errors_on_save": true

If there are errors in the file, a quick panel will appear which shows the error message, line number and source code for each error. The starting location of all errors on the line are marked with "^". Selecting an error in the quick panel jumps directly to the location of the first error on that line.

While editing a file, you can quickly move to the next/previous lint error with the following key equivalents:

* **OS X**::

    next: Control+Command+e
    prev: Control+Command+Shift+e

* **Linux, Windows**::

    next: Control+Alt+e
    prev: Control+Alt+Shift+e

By default the search will wrap. You can turn wrapping off with the user setting::

    "sublimelinter_wrap_find": false

Linter-specific notes
~~~~~~~~~~~~~~~~~~~~~
Following are notes specific to individual linters that you should be aware of:

* **JavaScript** – This linter runs `jshint <http://jshint.org>`_ using JavaScriptCore on Mac OS X or node.js on other platforms, which can be downloaded from [the node.js site](http://nodejs.org/#download). After installation, if node cannot be found by SublimeLinter, you may have to set the path to node in the "sublimelinter\_executable\_map" setting. See "Configuring" below for info on SublimeLinter settings.

    You may want to modify the options passed to jshint. This can be done globally or on a per-project basis by using the **jshint_options** setting. Refer to the jshint.org site for more information on the configuration options available.

* **ruby** – If you are using rvm or rbenv, you will probably have to specify the full path to the ruby you are using in the ``sublimelinter_executable_map`` setting. See "Configuring" below for more info.

* **java** – Because it uses ``javac`` to do linting, each time you run the linter the entire dependency graph of the current file will be checked. Depending on the number of classes you import, this can be **extremely** slow. Also note that you **must** provide the ``-sourcepath``, ``-classpath``, ``-Xlint`` and ``{filename}`` arguments to ``javac`` in your per-project settings. See "Per-project settings" below for more information.

Configuring
-----------
There are a number of configuration options available to customize the behavior of SublimeLinter and its linters. For the latest information on what options are available, select the menu item ``Preferences->Package Settings->SublimeLinter->Settings - Default``. To change the options in your user settings, select the menu item ``Preferences->File Settings - User``.

Per-project settings
~~~~~~~~~~~~~~~~~~~~
SublimeLinter supports per-project/per-language settings. This is useful if a linter requires path configuration on a per-project basis. To edit your project settings, select the menu item ``Project->Edit Project``. If there is no "settings" object at the top level, add one and then add a "SublimeLinter" sub-object, like this::

    {
        "folders":
        [
            {
                "path": "/Users/aparajita/Projects/foo/src"
            }
        ],
        "settings":
        {
            "SublimeLinter":
            {
            }
        }
    }

Within the "SublimeLinter" object, you can add a settings object for each language. The language name must match the language item in the linter's CONFIG object, which can be found in the linter's source file in the SublimeLinter/sublimelinter/modules folder. Each language can have two settings:

* "working_directory" – If present and a valid absolute directory path, the working directory is set to this path before the linter executes. This is useful if you are providing linter arguments that contain paths and you want to use working directory-relative paths instead of absolute paths.
* "lint_args" – If present, it must be a sequence of string arguments to pass to the linter. If your linter expects a filename as an argument, use the argument "{filename}" as a placeholder. Note that if you provide this item, you are responsible for passing **all** required arguments to the linter.

For example, let's say we are editing a Java project and want to use the "java" linter, which requires a source path and class path. In addition, we want to ignore serialization errors. Our project settings might look like this::

    {
        "folders":
        [
            {
                "path": "/Users/aparajita/Projects/foo/src"
            }
        ],
        "settings":
        {
            "SublimeLinter":
            {
                "java":
                {
                    "working_directory": "/Users/aparajita/Projects/foo",

                    "lint_args":
                    [
                        "-sourcepath", "src",
                        "-classpath", "libs/log4j-1.2.9.jar:libs/commons-logging-1.1.jar",
                        "-Xlint", "-Xlint:-serial",
                        "{filename}"
                    ]
                }
            }
        }
    }


Customizing colors
~~~~~~~~~~~~~~~~~~
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
who tend to ignore lint errors), you can set the user setting::

    "sublimelinter_fill_outlines": true

When this is set true, lines that have errors will be colored with the background
and foreground color of the "sublime.<type>" theme style. Unless you have defined
those styles, this setting should be left false.

You may also mark lines with errors by putting an "x" in the gutter with the user setting::

    "sublimelinter_gutter_marks": true

To customize the colors used for highlighting errors and user notes, add the following
to your theme (adapting the color to your liking)::

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
If a linter does not seem to be working, you can check the ST2 console to see if it was enabled. When SublimeLinter is loaded, you will see messages in the console like this::

    Reloading plugin /Users/aparajita/Library/Application Support/Sublime Text 2/Packages/SublimeLinter/sublimelinter_plugin.py
    SublimeLinter: JavaScript loaded
    SublimeLinter: annotations loaded
    SublimeLinter: Objective-J loaded
    SublimeLinter: perl loaded
    SublimeLinter: php loaded
    SublimeLinter: python loaded
    SublimeLinter: ruby loaded
    SublimeLinter: pylint loaded

The first time a linter is asked to lint, it will check to see if it can be enabled. You will then see messages like this::

    SublimeLinter: JavaScript enabled (using JavaScriptCore)
    SublimeLinter: Ruby enabled (using "ruby" for executable)

Let's say the ruby linter is not working. If you look at the console, you may see a message like this::

    SublimeLinter: ruby disabled ("ruby" cannot be found)

This means that the ruby executable cannot be found on your system, which means it is not installed or not in your executable path.

Creating New Linters
--------------------
If you wish to create a new linter to support a new language, SublimeLinter makes it easy. Here are the steps involved:

* Create a new file in sublimelinter/modules. If your linter uses an external executable, you will probably want to copy perl.py. If your linter uses built in code, copy objective-j.py. The convention is to name the file the same as the language that will be linted.

* Configure the CONFIG dict in your module. See the comments in base\_linter.py for information on the values in that dict. You only need to set the values in your module that differ from the defaults in base\_linter.py, as your module's CONFIG is merged with the default. Note that if your linter uses an external executable that does not take stdin, setting 'input\_method' to INPUT\_METHOD\_TEMP\_FILE will allow interactive linting with that executable.

* If your linter uses built in code, override ``built_in_check()`` and return the errors found.

* Override ``parse_errors()`` and process the errors. If your linter overrides ``built_in_check()``, ``parse_errors()`` will receive the result of that method. If your linter uses an external executable, ``parse_errors()`` receives the raw output of the executable, stripped of leading and trailing whitespace.

If your linter has more complex requirements, see the comments for CONFIG in base\_linter.py, and use the existing linters as guides.
