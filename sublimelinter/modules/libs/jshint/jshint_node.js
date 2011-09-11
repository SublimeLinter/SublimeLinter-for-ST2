/*jshint node:true */

/*
    Created by Aparajita Fishman  (https://github.com/aparajita)

    This code is adapted from the node.js jshint module to work with stdin instead of a file,
    and to take jshint options from the command line rather than a file.

    ** Licensed Under **

    The MIT License
    http://www.opensource.org/licenses/mit-license.php

    usage: node /path/to/jshint_wrapper.js "{option1:true,option2:false}"
    */

var _fs = require('fs'),
    _sys = require('sys'),
    _path = require('path'),
    _jshint = require(_path.join(_path.dirname(process.argv[1]), 'jshint.js')),
    _config;

function _removeJsComments(str) {
    str = str || '';
    str = str.replace(/\/\*[\s\S]*(?:\*\/)/g, ''); //everything between "/* */"
    str = str.replace(/\/\/[^\n\r]*/g, ''); //everything after "//"
    return str;
}

function hint() {
    var code = '',
        config = JSON.parse(process.argv[2]);

    process.stdin.resume();
    process.stdin.setEncoding('utf8');

    process.stdin.on('data', function (chunk) {
        code += chunk;
    });

    process.stdin.on('end', function () {
        var results = [];

        if (!_jshint.JSHINT(code, config)) {
            _jshint.JSHINT.errors.forEach(function (error) {
                if (error) {
                    results.push(error);
                }
            });
        }

        _sys.puts(JSON.stringify(results));
        process.exit(0);
    });
}

hint();
