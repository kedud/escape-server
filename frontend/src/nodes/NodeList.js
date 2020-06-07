import * as React from "react";

import { NodeCard } from './NodeCard';
import { List } from 'react-admin';

class NodeGrid extends React.Component {

    render() {
        let { ids, data, basePath } = this.props;
        return (
            <div style={{ margin: '1em' }}>
            {ids.map(id =>
                <NodeCard id={id} record={data[id]} basePath={ basePath }/>
            )}
            </div>
        );
    }
}

export const NodeList = (props) => (
    <List title="All nodes" {...props}>
        <NodeGrid />
    </List>
);

export default NodeList;
