var eslint = require("./eslint").eslint;

exports.lint = function (code, config) {
    var results;

    config.rules = config.rules || {};

    try {
        results = eslint.verify(code, config).map(function (res) {
            return {
                line: res.line,
                character: res.column + 1,
                reason: res.message
            };
        });
    } catch (e) {
        results = [
            {line: 1, character: 1, reason: e.message}
        ];
    }

    return results;
};
