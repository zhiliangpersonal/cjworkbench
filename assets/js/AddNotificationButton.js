/**
 * Component which can be dragged to a data import module
 *     to attach a notification
 */

import React from 'react';
import PropTypes from 'prop-types'
import { DragSource } from 'react-dnd';


const spec = {
  beginDrag(props, monitor, component) {
    return {
      index: false,
      id: props.id,
      insert: true,
    }
  }
}

function collect(connect, monitor) {
  return {
    connectDragSource: connect.dragSource(),
    isDragging: monitor.isDragging()
  }
}

class AddNotificationButton extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {

    var header = (this.props.libraryOpen)
      ? <div className='d-flex flex-row align-items-center'>
          <div className='ml-icon-container ml-2'>
            <div className="icon-notification ml-icon"></div>
          </div>
          <div>
            <div className='content-5 ml-module-name'>Add data alert</div>
          </div>
        </div>
      : <div className='ml-icon-container mr-5' >
          <div className="icon-notification ml-icon" title='Add Notification'></div>
        </div>

    return this.props.connectDragSource(
      <div className='card'>
        <div className='second-level t-vl-gray d-flex'>
          {header}
          <div className='ml-handle'>
            <div className='icon-grip'></div>
          </div>
        </div>
      </div>
    )
  }
}

export default DragSource('notification', spec, collect)(AddNotificationButton)

AddNotificationButton.propTypes = {
  libraryOpen: PropTypes.bool.isRequired
};