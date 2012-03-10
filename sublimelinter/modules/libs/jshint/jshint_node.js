/*jshint node:true */

/*
    Created by Aparajita Fishman  (https://github.com/aparajita)

    This code is adapted from the node.js jshint module to work with stdin instead of a file,
    and to take jshint options from the command line rather than a file.

    ** Licensed Under **

    The MIT License
    http://www.opensource.org/licenses/mit-license.php

    usage: node /path/to/jshint_node.js ["{option1:true,option2:false}"]
    */

var _fs = require('fs'),
    _util = require('util'),
    _path = require('path'),
    _jshint = require(_path.join(_path.dirname(process.argv[1]), 'jshint.js'));

function hint(code, config)
{
    var results = [];

    try {
        if (!_jshint.JSHINT(code, config)) {
            _jshint.JSHINT.errors.forEach(function (error) {
                if (error) {
                    results.push(error);
                }
            });
        }
    }
    catch (e) {
        results.push({line: 1, character: 1, reason: e.message});

        _jshint.JSHINT.errors.forEach(function (error) {
            if (error) {
                results.push(error);
            }
        });
    }

    _util.puts(JSON.stringify(results));
    process.exit(0);
}

function run()
{
    var code = '',
        config = JSON.parse(process.argv[2] || '{}'),
        filename = process.argv[3] || '';

    if (filename)
    {
        hint(_fs.readFileSync(filename, 'utf-8'), config);
    }
    else
    {
        process.stdin.resume();
        process.stdin.setEncoding('utf8');

        process.stdin.on('data', function (chunk) {
            code += chunk;
        });

        process.stdin.on('end', function () {
            hint(code, config);
        });
    }
}

run();
