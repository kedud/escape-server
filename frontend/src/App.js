import React from 'react';
import './App.css';

import dataProvider from './dataProvider';
import { Admin, Resource, ListGuesser } from 'react-admin';

import nodes from './nodes';

const App = () => (
    <Admin dataProvider={dataProvider}>
        <Resource name="node"  {...nodes} />
    </Admin>
);

export default App;
