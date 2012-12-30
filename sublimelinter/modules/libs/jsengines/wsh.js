/*jshint evil: true, wsh: true, undef: true, unused: true, bitwise: false */

// usage:
//   cscript -nologo /path/to/wsh.js /path/to/linter/ ["{option1:true,option2:false}"]

var LINTER_PATH = WScript.Arguments(0).replace(/\/$/, '') + '/',
    exports = {};

var require = function(file) {
    var script, stream;

    //Load and eval script.
    try {
        stream = WScript.CreateObject('ADODB.Stream');
        stream.Charset = 'utf-8';
        stream.Open();
        stream.LoadFromFile(LINTER_PATH + file.replace(/\.js$/, '') + '.js');
        script = stream.ReadText();
        stream.close();
        eval(script);
    } catch (e) {
        WScript.StdOut.WriteLine('WSH: Could not load ' + file);
        WScript.Quit(-1);
    }

    return exports;
};

// Polyfill for JSON.
// Define a empty 'define' and 'define.c' to make the json3 work.
var define = function() {};
define.c = {};
require('../jsengines/json3.min');

// Polyfill for Array.prototype.forEach, copy from JSLINT
if (typeof Array.prototype.forEach !== 'function') {
    Array.prototype.forEach = function (f) {
        var i, length = this.length;
        for (i = 0; i < length; i += 1) {
            try {
                f(this[i]);
            } catch (ignore) {
            }
        }
    };
}

require('linter');

var process = function () {
    var config, code = '',
        results = [];

    try {
        config = JSON.parse(WScript.Arguments(1).replace(/\\/g, '"'));
    } catch (e) {
        config = {};
    }

    code = WScript.StdIn.ReadAll();

    //Line numbers are wrong as JSLINT skips blank lines in WSH.
    //Workaround: insert comments in blank lines.
    if (typeof exports.JSLINT === 'function') {
        code = code.replace(/^\n/gm, '//\n');
    }

    results = exports.lint(code, config);
    WScript.StdOut.WriteLine(JSON.stringify(results));
    WScript.Quit(1);
};

process();
