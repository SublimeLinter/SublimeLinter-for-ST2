/*jshint node: true */
/*globals LINTER_PATH load */

// This linter users the TypeScript BatchCompiler, which makes passing the arguments easier
// Though maybe we should just switch to normal typescript.js

var path = require("path");
var TypeScript = require("./tsc");


// these are used to fool TypeScripts IO
var filename = "";
var code = "";
var results = [];

// as long as the --parse option does not work, we have to deactivate file saving manually
TypeScript.IO._createFile = TypeScript.IO.createFile;
TypeScript.IO.createFile = function createFile(filepath) {
    return {
                Write: function (str) {},
                WriteLine: function (str) {},
                Close: function () {}
            };
};

// fool TypeScript to get the newest content from the editor
TypeScript.IO._readFile = TypeScript.IO.readFile;
TypeScript.IO.readFile = function readFile(filepath) {
    if(filepath === filename)
        return code;
    else
        return TypeScript.IO._readFile(filepath);
};

// Hack to find lib.d.ts
TypeScript.IO._dirName = TypeScript.IO.dirName;
TypeScript.IO.dirName = function dirName(filepath) {
    if(filepath.indexOf(path.sep + "jsengines" + path.sep + "node.js") !== -1)
    {
        var split = filepath.split(path.sep);
        split.pop(); split.pop();
        split.push("typescript");
        filepath = split.join(path.sep);
        return filepath;
    }
    else
        return TypeScript.IO._dirName(filepath);
};

// gotta stop TypeScript from quitting
TypeScript.IO.quit = function quit(code) {};


// intercept error messages - here the linter results are filled
TypeScript.IO.stderr.Write = function Write(str) {

    // yeah, the following could be a regular expression, but i didn't wanna run into trouble with filenames that contain parentheses
    str = str.substring(0, str.length-3);
    var lastParen = str.lastIndexOf("(");
    var fileName = str.substring(0, lastParen);
    var nums = str.substring(lastParen + 1).split(",");

    results.push({
        line: parseInt(nums[0], 10),
        character: parseInt(nums[1], 10),
        fileName: fileName,
        reason: ""
    });
};
TypeScript.IO.stderr.WriteLine = function WriteLine(str) {
    if(results[results.length-1])
        results[results.length-1].reason = str;
};

exports.lint = function (codeOrig, config) {
    results = [];

    code = codeOrig;
    filename = config.filename;

    // The BatchCompiler parses the arguments
    TypeScript.IO.arguments = [filename];

    // better for comparison
    filename = filename.replace(/\\/g, "/");

    try {
        // that's where the magic starts
        var batchCompile = new TypeScript.BatchCompiler(TypeScript.IO);
        batchCompile.batchCompile();
    } catch (e) {
        results.push({line: 1, character: 1, reason: e.message});
    } finally {

    }

    return results;
};
