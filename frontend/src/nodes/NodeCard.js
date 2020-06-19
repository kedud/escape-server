import React from "react";
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import { Button, Chip } from '@material-ui/core';

import { TextField } from "react-admin";

import { subscribeToNode, sendActionEvent } from '../api/socketIO';

const cardStyle = {
    width: 300,
    minHeight: 300,
    margin: '0.5em',
    display: 'inline-block',
    verticalAlign: 'top'
};

export class NodeCard extends React.Component {

    constructor(props) {
        super(props)
        this.state = { 
		    "last_ping": new Date(props.record.last_ping), 
		    "types": [],
		  };
       
    } 

    componentDidMount() {
    	subscribeToNode(this.props.id, (err, node) => {
    		let json = JSON.parse(node);
            this.setState({ 
		    	"last_ping": new Date(json.last_ping * 1000),
		    	"status": json.status,
		    	"types": json.types ? json.types : [],
			});
        });

        setInterval( () => {
	        let current_time = new Date();
			this.setState({ 
				"current_time": current_time, 
				});
		}, 100);
    }

    handleButtonClick(event, record) {
    	sendActionEvent(event, record.hostname);
    }

    render() {
        let { record } = this.props;
        return (
            <Card style={cardStyle}>
                <CardHeader
                    title={<TextField record={record} source="hostname" />}
                    subheader={<TextField record={record} source="url" />}
                />
               	<CardContent>
                {
                	this.state.status === "resolved"? 
                	(
                		<Chip label={ this.state.status } variant="default" />
                	) 
                	:
                	(
                		<Chip label={ this.state.status } variant="default" color="secondary"/>
            		)	
                }
                </CardContent>
								{ this.state.current_time && this.state.last_ping && (
									<CardContent>
									{
										this.state.current_time - this.state.last_ping < 2000 ? 
										(
											<Chip label={(this.state.current_time - this.state.last_ping)} variant="default" />
										) 
										:
										(
											<Chip label={(this.state.current_time - this.state.last_ping)} variant="default" color="secondary"/>
									)	
									}
										
									</CardContent>
								)}
                <CardActions style={{ textAlign: 'right' }}>
                { 
                	this.state.types.includes("actuator") ? 
                	(
                		<Button 
	                		variant="contained" 
	                		color="primary"
	                		onClick={() => this.handleButtonClick('action', record)}
                		>
	                		Action
	                	</Button>
                	)
                	:
                	(
                		<Button 
	                		variant="contained" 
	                		color="primary"
	                		disabled
	                		onClick={() => this.handleButtonClick('action', record)}
                		>
	                		Action
	                	</Button>
                	)
            	}
                	<Button 
                		variant="contained" 
                		color="secondary"
                		onClick={() => this.handleButtonClick('reboot', record)}
                	>
                		Restart Node
                	</Button>
                </CardActions>
            </Card>
        );
    }
}

export default NodeCard;
