module.exports = {
  parser : '@typescript-eslint/parser', // Specify the parser for TypeScript
  parserOptions : {
    ecmaVersion : 2020,
    sourceType : 'module',
  },
  extends : [
    'airbnb', // Use Airbnb's base config for React
    'plugin:@typescript-eslint/recommended', // Recommended TypeScript rules
  ],
  plugins : [ '@typescript-eslint', 'import-newlines' ], // Enable TypeScript, React, and React Hooks plugins
  rules : {
    // Customize any rules here
    '@typescript-eslint/no-require-imports' : 'off',
    'key-spacing' : [ 'error', {
      beforeColon : true, // Enforce spacing before colons in object literals
      afterColon : true, // Enforce spacing after colons in object literals
      mode : 'strict', // Enforce strict spacing rules
    } ],
    'array-bracket-spacing' : [ 'error', 'always' ], // Require spaces inside array brackets
    'object-curly-spacing' : [ 'error', 'always' ], // Require spaces inside curly braces
    'max-len' : [ 'error', { code : 160 } ], // Set maximum line length to 160 characters
    'no-unused-vars' : 'off', // Disable default no-unused-vars rule
    '@typescript-eslint/no-unused-vars' : [ 'error' ], // Enable the TypeScript version of the rule
    'import/extensions' : [
      'error',
      'ignorePackages',
      {
        ts : 'never',
        js : 'never',
      },
    ],
    'import/no-extraneous-dependencies' : [ 'error', { devDependencies : true } ],
    'import-newlines/enforce' : [ 'error', {
      items : 3, // Number of imports before enforcing new lines. Must be kept in sync with airbnb's object-curly-newline rule.
      'max-len' : 160, // Maximum line length for imports. Must be kept in sync with max-len rule above.
      semi : true, // Imports should end with a semicolon
    } ],
    'no-console': 'off', // Services can and should perform logging via console
  },
  settings : {
    'import/resolver' : {
      typescript : {}, // Use tsconfig.json for module resolution
    },
  },
};
