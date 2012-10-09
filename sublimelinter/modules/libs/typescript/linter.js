/*jshint node: true */
/*globals LINTER_PATH load */

"use strict";

var fs = require("fs");


var path = require("path");
var TypeScript = require("./typescript");
var IO = require("./IO");
var CommandLineHost = require("./CommandLineHost");


var compilerFilePath = IO.getExecutingFilePath();
var binDirPath = IO.dirName(compilerFilePath);

var tsLinterPath = path.normalize(binDirPath + path.sep + ".." + path.sep + "typescript");

// ================================================


var errorRegex = /(.*)\(([0-9]+,[0-9]+)\): (.*)/;

/**
 * Handles parser errors
 * INFO: TypeScript issues errors in two ways: 1.) per errorOutput and 2.) per errorCallback
 *       this analyer is for the errorOutput
 *
 * @constructor
 *
 * @param {Compiler} compiler The connected compiler
 */
function ParserErrorAnalyser(compiler)
{
    this.compiler = compiler;
    this.currentLine = "";
}

ParserErrorAnalyser.prototype.Write = function Write(str) { 
    this.currentLine += str;
};

ParserErrorAnalyser.prototype.WriteLine = function WriteLine(str) { 
    this.currentLine += str;

    var res = this.currentLine.match(errorRegex);

    // we found a file-specific error
    if(res) {

        var lineCol = res[2].split(",");
        var line = parseInt(lineCol[0], 10);
        var col = parseInt(lineCol[1], 10);

        if(filenamesAreEqual(this.compiler.lintedFile.path, res[1])) {
            this.compiler.errors.push(createError(line, col, res[3], res[1]));
        } else {
            var otherMessage = res[1] + " (" + line + "," + col + "): " + res[3];
            this.compiler.errors.push(createError(1, 1, otherMessage, res[1]));
        }

    // we found some weird error
    } else {
        this.compiler.errors.push(createError(1, 1, this.currentLine, ""));
    }


    // reset the current line
    this.currentLine = "";
};

ParserErrorAnalyser.prototype.Close = function Close(str) {};


function createError(line, character, reason, filename) {
    return {
        line: line, 
        character: character, 
        reason: reason,
        filename: filename
    };
}

function filenamesAreEqual(fn1, fn2) {
    return TypeScript.switchToForwardSlashes(fn1) === TypeScript.switchToForwardSlashes(fn2);
}


// ================================================

var outFile = { 
    Write: function (str) {}, 
    WriteLine: function (str) {}, 
    Close: function () {} 
};


/**
 * Compiler for parsing TypeScript files
 *
 * @param {[type]} compilationSettings [description]
 */
function Compiler(compilationSettings, lintedFile)
{
    this.compilationSettings = compilationSettings;
    this.lintedFile = lintedFile;
    this.compilationEnvironment = new TypeScript.CompilationEnvironment(this.compilationSettings, IO);

    var _this = this;

    // this is where parser errors arrive
    this.parserErrors = new ParserErrorAnalyser(this);

    if(this.compilationSettings.useDefaultLib) {
        var code = new TypeScript.SourceUnit(tsLinterPath + path.sep + "lib.d.ts", null);
        this.compilationEnvironment.code.push(code);
    }

    this.resolver = null;
    this.resolvedEnvironment = null;
    this.errors = [];
}

/**
 * Resolves file dependencies (included modules, etc)
 */
Compiler.prototype.resolve = function resolve() {
    this.commandLineHost = new CommandLineHost();
    this.resolver = new TypeScript.CodeResolver(this.compilationEnvironment);
    this.resolvedEnvironment = this.commandLineHost.resolveCompilationEnvironment(this.compilationEnvironment, this.resolver, true);
    
    var i;
    for(i = 0; i < this.compilationEnvironment.residentCode.length; i++) {
        if(!this.commandLineHost.isResolved(this.compilationEnvironment.residentCode[i].path)) {
            this.parserErrors.WriteLine("Error reading file \"" + this.compilationEnvironment.residentCode[i].path + "\": File not found");
        }
    }
    for(i = 0; i < this.compilationEnvironment.code.length; i++) {
        if(!this.commandLineHost.isResolved(this.compilationEnvironment.code[i].path)) {
            this.parserErrors.WriteLine("Error reading file \"" + this.compilationEnvironment.code[i].path + "\": File not found");
        }
    }
};

/**
 * Parses a SourceUnit
 *
 * @param  {??}      code          SourceUnit to parse
 * @param  {boolean} addAsResident ??
 */
Compiler.prototype.consumeUnit = function (code, addAsResident) {
    try  {
        if(!this.compilationSettings.resolve) {
            code.content = IO.readFile(code.path);
        }
        if(code.content) {
            if(this.compilationSettings.parseOnly) {
                this.compiler.parseUnit(code.content, code.path);
            } else {
                if(this.compilationSettings.errorRecovery) {
                    this.compiler.parser.setErrorRecovery(outFile, -1, -1);
                }
                this.compiler.addUnit(code.content, code.path, addAsResident);
            }
        }
    } catch (err) {
        this.compiler.errorReporter.hasErrors = true;
        this.parserErrors.WriteLine(err.message + " " + err.stack);
    }
};

/**
 * Error callback for handling found errors
 *
 * @param  {number} minChar   The first character of the found problem
 * @param  {number} charLen   Number of charachters of the problem
 * @param  {string} message   Problem message
 * @param  {number} unitIndex Index of the source unit (for retrieving the filename, etc.)
 */
Compiler.prototype.errorCallback = function (minChar, charLen, message, unitIndex) {
    this.compiler.errorReporter.hasErrors = true;
    var errorFilename = this.resolvedEnvironment.code[unitIndex].path;

    var line = this.compiler.parser.scanner.line;
    var col = this.compiler.parser.scanner.col;

    if(filenamesAreEqual(this.lintedFile.path, errorFilename)) {
        this.errors.push(createError(line, col, message, errorFilename));
    } else {
        var otherMessage = errorFilename + " (" + line + "," + col + "): " + message;
        this.errors.push(createError(1, 1, otherMessage, errorFilename));
    }
};

/**
 * Compiles and does the final typechecking
 */
Compiler.prototype.compile = function compile() {
    this.compiler = new TypeScript.TypeScriptCompiler(outFile, outFile);
    

    // our error reporter
    this.compiler.setErrorOutput(this.parserErrors);
    this.compiler.setErrorCallback(this.errorCallback.bind(this));

    // parse all the units that have been resolved
    for(var iResCode = 0; iResCode < this.resolvedEnvironment.residentCode.length; iResCode++) {
        if(!this.compilationSettings.parseOnly) {
            this.consumeUnit(this.resolvedEnvironment.residentCode[iResCode], true);
        }
    }
    for(var iCode = 0; iCode < this.resolvedEnvironment.code.length; iCode++) {
        if(!this.compilationSettings.parseOnly || (iCode > 0)) {
            this.consumeUnit(this.resolvedEnvironment.code[iCode], false);
        }
    }

    // do the typechecking
    this.compiler.typeCheck();
};

/**
 * Adds a Source code unit to the compilation
 *
 * @param {TypeScript.SourceUnit} sourceUnit Source unit to add
 */
Compiler.prototype.addSourceUnit = function addSourceUnit(sourceUnit) {
    this.compilationEnvironment.code.push(sourceUnit);
};


/**
 * Perform the linting
 *
 * @param  {string} codeOrig Code to lint
 * @param  {object} config   Configuration parameters
 *
 * @return {Array}          Array of lint results
 */
exports.lint = function (codeOrig, config) {

    try {
        // that's where the magic starts

        var lintedFile = {
            content: codeOrig,
            path: config.filename
        };

        // creating the compiler
        var compilationSettings = new TypeScript.CompilationSettings();
        var compiler = new Compiler(compilationSettings, lintedFile);
        
        // adding the code of the current file
        var sourceUnit = new TypeScript.SourceUnit(lintedFile.path, null);
        compiler.addSourceUnit(sourceUnit);
        
        // compile
        compiler.resolve();
        compiler.compile();
        
        return compiler.errors;

    } catch (e) {
         return [{line: 1, character: 1, reason: e.message + " " + e.stack}];
    } 
};

//console.log(exports.lint());