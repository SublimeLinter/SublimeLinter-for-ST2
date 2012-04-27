/*jshint node: true */
/*globals LINTER_PATH load */

var JSHINT = require("./jshint").JSHINT,
    path = require('path'),
    fs = require('fs');

var rootPath = path.resolve("/");

function existsSync() {
    var obj = fs.existsSync ? fs : path;
    return obj.existsSync.apply(obj, arguments);
}

/**
 * This function searches for a file with a specified name, it starts
 * with the dir passed, and traverses up the filesystem until it either
 * finds the file, or hits the root
 *
 * @param {String} name  Filename to search for (.jshintrc, .jshintignore)
 * @param {String} dir   Defaults to process.cwd()
 */
function _searchFile(name, dir) {
    var filename = path.normalize(path.join(dir, name));

    if (existsSync(filename)) {
        return filename;
    }

    return dir === rootPath ?
        null : _searchFile(name, path.normalize(path.join(dir, "..")));
}

function _findConfig(filename) {
    var name = ".jshintrc",
        projectConfig = _searchFile(name, filename),
        homeConfig = path.normalize(path.join(process.env.HOME, name));

    if (projectConfig) {
        return projectConfig;
    }

    // if no project config, check $HOME
    if (existsSync(homeConfig)) {
        return homeConfig;
    }

    return false;
}

exports.lint = function (code, config, lintPath, filename) {
    var results = [];
    
    // if filename exists check for .jshintrc for config
    if (filename) {
        var jshintrc = _findConfig(filename);
        if (jshintrc) {
            config = JSON.parse(fs.readFileSync(jshintrc));
        }
    }

    try {
        JSHINT(code, config);
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
