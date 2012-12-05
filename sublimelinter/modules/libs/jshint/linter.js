/*jshint node: true */
/*globals LINTER_PATH load */

var JSHINT = require("./jshint").JSHINT;

exports.lint = function (code, config) {
    var globals,
        results = [];

    if (config.globals) {
        globals = config.globals;
        delete config.globals;
    }

    try {
        JSHINT(code, config, globals);
    } catch (e) {
        results.push({line: 1, character: 1, reason: e.message});
    } finally {
        JSHINT.errors.forEach(function (error) {
            if (error) {
                results.push(error);
            }
        });
    }

    return results;
};
