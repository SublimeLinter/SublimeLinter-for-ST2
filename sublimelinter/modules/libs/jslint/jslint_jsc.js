/*jshint boss: true, evil: true */
/*globals load quit readline JSHINT */

// usage:
//   jsc ${envHome}/jsc.js -- ${lineCount} {option1:true,option2:false} ${envHome}
var envHome = '';

if (arguments.length > 2) {
    envHome = arguments[2].toString().replace(/\/env$/, '/');
}

load(envHome + "jslint.js");

if (typeof(JSLINT) === 'undefined') {
    print('jslint: Could not load jslint.js, tried "' + envHome + 'jslint.js".');
    quit();
}

var process = function (args) {
    var lineCount = parseInt(args[0], 10),
        opts = (function (arg) {
            switch (arg) {
            case undefined:
            case '':
                return {};
            default:
                return eval('(' + arg + ')');
            }
        })(args[1]);

    if (isNaN(lineCount)) {
        print('jslint: Must provide number of lines to read from stdin.');
        quit();
    }

    var input = readline();

    for (var i = 0; i < lineCount; ++i) {
        input += '\n' + readline();
    }

    var results = [],
        err;

    try
    {
        if (!JSLINT(input, opts)) {
            for (i = 0; err = JSLINT.errors[i]; i++) {
                results.push(err);
            }
        }
    }
    catch (e) {
        results.push({line: 1, character: 1, reason: e.message});

        for (i = 0; err = JSLINT.errors[i]; i++) {
            results.push(err);
        }
    }

    print(JSON.stringify(results));
    quit();
};

process(arguments);
