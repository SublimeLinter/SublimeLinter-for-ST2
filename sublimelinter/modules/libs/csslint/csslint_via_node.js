/*csslint node:true */

/*
    Created by Aparajita Fishman  (https://github.com/aparajita)

    This code is adapted from the node.js csslint module to work with stdin instead of a file,
    and to take csslint options from the command line rather than a file.

    ** Licensed Under **

    The MIT License
    http://www.opensource.org/licenses/mit-license.php

    usage: node /path/to/csslint_via_node.js ["{option1:true,option2:false}"]

    */

var _fs = require('fs'),
    _util = require('util'),
    _path = require('path'),
    _csslint = require(_path.join(_path.dirname(process.argv[1]), 'csslint-node.js'));

function lint(code, config)
{
    var results = [];
    var ruleset = {};

    // rules that are 'false' will be ignored.
    for (var ruleName in config['rules']) {
        if (config['rules'][ruleName] === 'warning') {
            ruleset[ruleName] = 1;
        }
        else if (config['rules'][ruleName] === 'error') {
            ruleset[ruleName] = 2;
        }
    }
    
    var report = _csslint.CSSLint.verify(code, ruleset);

    report.messages.forEach(function (message) {
        if (message) {

            // message.type // warning|error
            // message.line
            // message.col
            // message.message
            // message.evidence // Requires sanitizing as it can include CR, LF 
            // message.rule // The rule object 
            
            // We don't pass on the rollup messages
            if (message.rollup !== true) {
                results.push({
                        'line': message.line,
                        'character': message.col,
                        'reason': message.type + ' ' + message.message
                    } );
            }
        }
    });

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
        lint(_fs.readFileSync(filename, 'utf-8'), config);
    }
    else
    {
        process.stdin.resume();
        process.stdin.setEncoding('utf8');

        process.stdin.on('data', function (chunk) {
            code += chunk;
        });

        process.stdin.on('end', function () {
            lint(code, config);
        });
    }
}

run();