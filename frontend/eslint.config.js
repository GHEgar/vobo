import base from '@npmegar/eslint-config';
import react from '@npmegar/eslint-config/react';
import reactApp from '@npmegar/eslint-config/react-app';

export default [
    { ignores: ['public/**'] },
    ...base,
    ...react,
    ...reactApp,
];
