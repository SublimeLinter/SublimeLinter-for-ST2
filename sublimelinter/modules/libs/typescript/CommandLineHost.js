var CommandLineHost = (function () {
    function CommandLineHost() {
        this.pathMap = {
        };
        this.resolvedPaths = {
        };
    }
    CommandLineHost.prototype.isResolved = function (path) {
        return this.resolvedPaths[this.pathMap[path]] != undefined;
    };
    CommandLineHost.prototype.resolveCompilationEnvironment = function (preEnv, resolver, traceDependencies) {
        var _this = this;
        var resolvedEnv = new TypeScript.CompilationEnvironment(preEnv.compilationSettings, preEnv.ioHost);
        var nCode = preEnv.code.length;
        var nRCode = preEnv.residentCode.length;
        var postResolutionError = function (errorFile, errorMessage) {
            TypeScript.CompilerDiagnostics.debugPrint("Could not resolve file '" + errorFile + "'" + (errorMessage == "" ? "" : ": " + errorMessage));
        };
        var resolutionDispatcher = {
            postResolutionError: postResolutionError,
            postResolution: function (path, code) {
                if(!_this.resolvedPaths[path]) {
                    resolvedEnv.code.push(code);
                    _this.resolvedPaths[path] = true;
                }
            }
        };
        var residentResolutionDispatcher = {
            postResolutionError: postResolutionError,
            postResolution: function (path, code) {
                if(!_this.resolvedPaths[path]) {
                    resolvedEnv.residentCode.push(code);
                    _this.resolvedPaths[path] = true;
                }
            }
        };
        var path = "";
        for(var i = 0; i < nRCode; i++) {
            path = TypeScript.switchToForwardSlashes(preEnv.ioHost.resolvePath(preEnv.residentCode[i].path));
            this.pathMap[preEnv.residentCode[i].path] = path;
            resolver.resolveCode(path, "", false, residentResolutionDispatcher);
        }
        for(var i = 0; i < nCode; i++) {
            path = TypeScript.switchToForwardSlashes(preEnv.ioHost.resolvePath(preEnv.code[i].path));
            this.pathMap[preEnv.code[i].path] = path;
            resolver.resolveCode(path, "", false, resolutionDispatcher);
        }
        return resolvedEnv;
    };
    return CommandLineHost;
})();

var TypeScript = require("./typescript");
module.exports = exports = CommandLineHost;