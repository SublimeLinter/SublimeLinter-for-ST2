/*jshint boss: true, evil: true */

// usage:
//   jsc ${envHome}/jsc.js -- ${lineCount} {option1:true,option2:false} ${envHome}
var envHome = '';

if (arguments.length > 2) {
    envHome = arguments[2].toString().replace(/\/env$/, '/');
}

load(envHome + "jshint.js");

if (typeof(JSHINT) === 'undefined') {
    print('jshint: Could not load jshint.js, tried "' + envHome + 'jshint.js".');
    quit();
}

var process = function(args) {
    var lineCount = parseInt(args[0], 10),
        opts  = (function(arg){
            switch (arg) {
            case undefined:
            case '':
                return {};
            default:
                return eval('(' + arg + ')');
            }
        })(args[1]);

    if (isNaN(lineCount)) {
        print('jshint: Must provide number of lines to read from stdin.');
        quit();
    }

    var input = readline();

    for (var i = 0; i < lineCount; ++i) {
        input += '\n' + readline();
    }

    var results = [];

    if (!JSHINT(input, opts)) {
        var err;

        for (i = 0; err = JSHINT.errors[i]; i++) {
            results.push(err);
        }
    }

    print(JSON.stringify(results));
    quit();
};

process(arguments);
