var eslint = require("./eslint/lib/eslint");

exports.lint = function (code, config) {
    var results;

    config.rules = config.rules || {};

    try {
        results = eslint.verify(code, config);
    } catch (e) {
        results = [
            {line: 1, character: 1, reason: e.message}
        ];
    }

    return results;
};
