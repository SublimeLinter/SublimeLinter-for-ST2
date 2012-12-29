/*jshint evil: true, wsh: true, undef: true, unused: true, bitwise: false */
/*global JSHINT JSLINT CSSLint */

// usage:
//   cscript -nologo /path/to/wsh.js /path/to/linter/ ["{option1:true,option2:false}"]

var LINTER_PATH = WScript.Arguments(0).replace(/\/$/, '') + '/',
    JSON_PATH = LINTER_PATH + '../jsengines/',
    linter = {};

var require = function(file, path) {
    var script = '';

    path = path || LINTER_PATH;

    //Load and eval script.
    try {
        var stream = WScript.CreateObject('ADODB.Stream');
        stream.Charset = 'utf-8';
        stream.Open();
        stream.LoadFromFile(path + file.replace(/\.js$/, '') + '.js');
        script = stream.ReadText();
        stream.close();
        eval(script);
    } catch (e) {
        WScript.StdOut.WriteLine('WSH: Could not load ' + file);
        WScript.Quit(-1);
    }

    //Pass the actual linter function to linter object.
    if (typeof JSHINT !== 'undefined') {
        linter.JSHINT = JSHINT;
    } else if (typeof JSLINT !== 'undefined') {
        linter.JSLINT = JSLINT;
    } else if (typeof CSSLint !== 'undefined') {
        linter.CSSLint = CSSLint;
    }

    return linter;
};

// Polyfill for JSON.
require('json3.min', JSON_PATH);

// Define exports here, avoid conflicating with json3.
var exports = {};

// Polyfill for Array.prototype.forEach.
if (!Array.prototype.forEach) {
    Array.prototype.forEach = function (callback, thisArg) {
        var T, k;
        var O = Object(this);
        var len = O.length >>> 0;
        if ({}.toString.call(callback) !== '[object Function]') {
            throw new TypeError(callback + ' is not a function');
        }
        if (thisArg) {
            T = thisArg;
        }
        k = 0;
        while (k < len) {
            var kValue;
            var Pk = String(k);
            var kPresent = Pk in O;
            if (kPresent) {
                kValue = O[Pk];
                callback.call(T, kValue, k, O);
            }
            k++;
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
    if (typeof linter.JSLINT === 'function') {
        code = code.replace(/^\n/gm, '//\n');
    }

    results = exports.lint(code, config);
    WScript.StdOut.WriteLine(JSON.stringify(results));
    WScript.Quit(1);
};

process();
