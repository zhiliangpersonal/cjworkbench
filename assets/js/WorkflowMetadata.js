// WorkflowMetadata: that line below the workflow title
// which shows owner, last modified date, public/private

import React from 'react'
import PropTypes from 'prop-types'
import {
  Button,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter
} from 'reactstrap'
import { timeDifference } from './utils'


export default class WorkflowMetadata extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      isPublic: this.props.isPublic,
      privacyModalOpen: false
    };
    this.setPublic = this.setPublic.bind(this);
    this.togglePrivacyModal = this.togglePrivacyModal.bind(this);
  }

  // Listens for changes from parent
  componentWillReceiveProps(nextProps) {
    if (nextProps.workflow === undefined) {
      return false;
    }

    this.setState({
      isPublic: nextProps.isPublic
    });
  }

  setPublic(isPublic) {
    this.props.api.setWorkflowPublic(this.props.workflow.id, isPublic)
    .then(() => {
      this.setState({isPublic: isPublic});
      // hard reload, to ensure consistency of state with Share button in parent Navbar component
      location.reload();
    })
    .catch((error) => {
      console.log('Request failed', error);
    });
  }

  togglePrivacyModal() {
    this.setState({ privacyModalOpen: !this.state.privacyModalOpen });
  }

  renderPrivacyModal() {
    if (!this.state.privacyModalOpen) {
      return null;
    }

    return (
      <Modal isOpen={this.state.privacyModalOpen} toggle={this.togglePrivacyModal}>
        <ModalHeader toggle={this.togglePrivacyModal} className='dialog-header' >
          <span className='t-d-gray title-4'>PRIVACY SETTING</span>
        </ModalHeader>
        <ModalBody className='dialog-body'>
          <div className="row d-flex align-items-center mb-5">
            <div className="col-sm-3">
              <div
                className={"action-button " + (this.state.isPublic ? "button-full-blue" : "button-gray test-button-gray") }
                onClick={() => {this.setPublic(true); this.togglePrivacyModal()}}>
                  Public
              </div>
            </div>
            <div className="col-sm-9">
              <div className='info-2'>Anyone can access and duplicate the workflow or any of its modules</div>
            </div>
          </div>
          <div className="row d-flex align-items-center">
            <div className="col-sm-3">
              <div
                className={"action-button " + (!this.state.isPublic ? "button-full-blue" : "button-gray test-button-gray")}
                onClick={() => {this.setPublic(false); this.togglePrivacyModal()}}>
                  Private
              </div>
            </div>
            <div className="col-sm-9">
              <div className='info-2'>Only you can access and edit the workflow</div>
            </div>
          </div>
        </ModalBody>
        <div className='dialog-footer modal-footer'>
          <div onClick={this.togglePrivacyModal} className='action-button button-gray'>Cancel</div>
        </div>
      </Modal>
    );
  }

  render() {

    var now = this.props.test_now || new Date();

    //giving a different style to metadata if it's displayed in WF list
    var publicColor = this.props.inWorkflowList? 't-f-blue': 't-white-u';
    var metaColor = this.props.inWorkflowList? 't-m-gray': 't-white';

    // only list User attribution if one exists & is not just whitespace
    var user = this.props.workflow.owner_name.trim();
    var attribution = user.length
      ? <span>
          <li className="list-inline-item content-3">by {user}</li>
          <span className='metadataSeparator'>-</span>
        </span>
      : null
    var modalLink = (this.props.workflow.read_only)
      ? null
      : <div className="list-inline-item test-button d-flex content-3 " onClick={this.togglePrivacyModal}>
          <span className='metadataSeparator'>-</span>
          <div className={''+publicColor}>{this.state.isPublic ? 'public' : 'private'}</div>
        </div>

    return (
      <div className=''>
        <ul className={"list-inline workflow-meta content-3 "+ metaColor}>
           {attribution}
          <li className={"list-inline-item content-3 "+ metaColor}>
            Updated {timeDifference(this.props.workflow.last_update, now)}
          </li>
          <li className="list-inline-item content-3">
          {modalLink}
          </li>
        </ul>
        { this.renderPrivacyModal() }
      </div>
    );
  }
}

WorkflowMetadata.propTypes = {
  workflow:   PropTypes.object.isRequired,
  api:        PropTypes.object.isRequired,
  isPublic:   PropTypes.bool.isRequired,
  inWorkflowList: PropTypes.bool, //change styling for use inside WF list
  test_now:   PropTypes.object  // optional injection for testing, avoid time zone issues for Last Update time
};
