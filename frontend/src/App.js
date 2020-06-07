import React from 'react';
import { put } from 'redux-saga/effects';
import './App.css';

import dataProvider from './dataProvider';
import { Admin, Resource, ListGuesser, showNotification } from 'react-admin';

import nodes from './nodes';

import { socketIoEvents } from './api/socketIO';

class App extends React.Component  {

	constructor(props) {
		super(props);
		
	}

	componentDidMount() {
		socketIoEvents((event) => {
			console.log("socketIO event: " + event);
			put(showNotification("socketIO event: " + event));
		}
		)
	}

	render() {
		return(
		    <Admin dataProvider={dataProvider}>
		        <Resource name="node"  {...nodes} />
		    </Admin>
		);
	}
}

export default App;
