import js from '@eslint/js';
import globals from 'globals';

export default [
    {
        ignores: ['admin/**', 'uploads/**', 'logs/**'],
    },
    js.configs.recommended,
    {
        files: ['assets/js/**/*.js', 'tests/**/*.js'],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: 'module',
            globals: {
                ...globals.browser,
                ...globals.jquery,
                console: true,
            },
        },
        rules: {
            'no-console': ['warn', { allow: ['info', 'warn', 'error'] }],
        },
    },
    {
        files: ['tests/**/*.js'],
        languageOptions: {
            globals: {
                ...globals.node,
            },
        },
    },
];
