module.exports = {
  parser: '@typescript-eslint/parser', // Specify the parser for TypeScript
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true, // Enable JSX parsing
    },
  },
  extends: [
    'airbnb', // Use Airbnb's base config for React
    'plugin:@typescript-eslint/recommended', // Recommended TypeScript rules
    'plugin:react/recommended', // Recommended React rules
    'plugin:react-hooks/recommended', // Recommended React Hooks rules
  ],
  plugins: ['@typescript-eslint', 'react', 'react-hooks'], // Enable TypeScript, React, and React Hooks plugins
  rules: {
    // Customize any rules here
    'no-unused-vars': 'off', // Disable default no-unused-vars rule
    '@typescript-eslint/no-unused-vars': ['error'], // Enable the TypeScript version of the rule
    'react/prop-types': 'off', // Disable prop-types check since TypeScript already handles types
    'react/react-in-jsx-scope': 'off', // React 17+ doesn't require `import React` in every file
    'import/extensions': [
      'error',
      'ignorePackages',
      {
        ts: 'never',
        tsx: 'never',
        js: 'never',
        jsx: 'never',
      },
    ],
    'react/jsx-filename-extension': ['error', { extensions: ['.js', '.jsx', '.ts', '.tsx'] }],
    'import/no-extraneous-dependencies': ['error', { devDependencies: true }],
    'react/require-default-props': ['error', {
      functions: 'defaultArguments', // Default props must now be defined in arguments - .defaultProps was removed in React 19
    }],
  },
  settings: {
    react: {
      version: 'detect', // Automatically detect React version
    },
    'import/resolver': {
      typescript: {}, // Use tsconfig.json for module resolution
    },
  },
};
