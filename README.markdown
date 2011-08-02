SublimeLint
=========

A code-validating plugin with inline highlighting for the [Sublime Text 2](http://sublimetext.com "Sublime Text 2") editor.

Supports the following languages:

* Python - native, moderately-complete lint
* PHP - syntax checking via "php -l"
* Perl - syntax+deprecation checking via "perl -c"
* Ruby - syntax checking via "ruby -wc"

Installing
-----

*Without Git:* Download the latest source from http://github.com/aroberge/sublimelint and copy sublimelint_plugin.py and the sublimelint/ folder to your Sublime Text "User" packages directory.

*With Git:* Clone the repository in your Sublime Text Packages directory (located one folder above the "User" directory)

> git clone git://github.com/lunixbochs/sublimelint.git


The "User" packages directory is located at:

* Windows:
    %APPDATA%/Sublime Text 2/Packages/User/
* OS X:
    ~/Library/Application Support/Sublime Text 2/Packages/User/
* Linux:
    ~/.Sublime Text 2/Packages/User/

Using
-----

For detailed, up to date instructions, enter the following at the console

    view.run_command("lint")
or
    view.run_command("lint", "help")

1. To enable the plugin to work by default, you need to set a user preference "sublimelint" to true.
2. You can turn on/off the linter via a command view.run_command("linter_on") (or "linter_off") - even if you have not set a user preference before.

Note that the linter normally works in a background thread and is constantly refreshing when enabled.

3. To run a linter "once" (i.e. not always on in the background), you use
view.run_command("run_linter"), "LINTER") where "LINTER" is one of "Python", "PHP" or "pylint".
4. If you run a linter via a commmand as in 3. above, the realtime linter is automatically disabled. To reset to its previous state (on or off) AND to clear all visible "errors", you use the command
view.run_command("reset_linter").

Python and PEP8
---------------

If you use SublimeLint for pep8 checks, you can ignore some of the conventions,
with the user preference "pep8_ignore".

Here is an example:

    "pep8_ignore":
        [
            "E501"
        ],

This configuration will ignore the long lines convention. You can see the list
of codes (as "E501") in [this file](https://github.com/jcrocholl/pep8/blob/master/pep8.py).

Python and PyFlakes
-------------------

If you use SublimeLint for pyflakes checks, you can ignore some of the "undefined name xxx" errors (comes in handy if you work with post-processors, globals/builtins available only at runtime, etc.). You can control what names will be ignored with the user preference "pyflakes_ignore".

Example:

    "pyflakes_ignore":
        [
            "some_custom_builtin_o_mine",
            "A_GLOBAL_CONSTANT"
        ],
