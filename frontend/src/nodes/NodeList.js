import * as React from "react";
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import PersonIcon from '@material-ui/core/Avatar';
import { List, TextField, DateField, ReferenceField, EditButton } from "react-admin";

const cardStyle = {
    width: 300,
    minHeight: 300,
    margin: '0.5em',
    display: 'inline-block',
    verticalAlign: 'top'
};

const NodeGrid = ({ ids, data, basePath }) => (
    <div style={{ margin: '1em' }}>
    {ids.map(id =>
        <Card key={id} style={cardStyle}>
            <CardHeader
                title={<TextField record={data[id]} source="hostname" />}
                subheader={<TextField record={data[id]} source="id" />}
            />
            <CardContent>
                <TextField record={data[id]} source="url" />
            </CardContent>
            <CardContent>
                <TextField record={data[id]} source="last_ping" />
            </CardContent>
            <CardActions style={{ textAlign: 'right' }}>
                <EditButton resource="nodes" basePath={basePath} record={data[id]} />
            </CardActions>
        </Card>
    )}
    </div>
);

NodeGrid.defaultProps = {
    data: {},
    ids: [],
};

export const NodeList = (props) => (
    <List title="All nodes" {...props}>
        <NodeGrid />
    </List>
);

export default NodeList;
