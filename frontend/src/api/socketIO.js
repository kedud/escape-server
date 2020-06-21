import openSocket from 'socket.io-client';

const socket = openSocket('http://' + window.location.hostname + ':5000');


function socketIoEvents(cb) {
	socket.on('connect', (node) => {
		cb('connect');
	});
	socket.on('disconnect', (node) => {
		cb('disconnect');
	});
}

function subscribeToNode(hostname, cb) {
	//console.log("subscribeToNode hostname: ", hostname);
	socket.on(hostname, (node) => {
		//console.log('subscribeToNode', node);
		console.log('http://' + window.location.hostname + ':5000')
		cb(null, node);
	});
}

function sendActionEvent(event, hostname) {
	socket.emit(event, { hostname: hostname });
}

export { socketIoEvents, subscribeToNode, sendActionEvent };