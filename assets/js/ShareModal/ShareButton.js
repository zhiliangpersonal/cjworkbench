import React from 'react'
import PropTypes from 'prop-types'
import ShareModal from './index'
import { t } from '@lingui/macro'
import { withI18n } from '@lingui/react'
/**
 * A <button> that opens/closes a ShareModal.
 *
 * When the user clicks the <button>, the modal opens. The user can close
 * the modal, and then the <button> becomes clickable again.
 */
export function ShareButton ({ className, children }) {
  const [isOpen, setIsOpen] = React.useState(false)
  const open = React.useCallback(() => setIsOpen(true))
  const close = React.useCallback(() => setIsOpen(false))

  return (
    <>
      <button
        type='button'
        className='share-button'
        name='share'
        title={this.props.i18n._(t('workflow.visibility.sharingTitle')`Change Workflow sharing`)}
        onClick={open}
      >
        {children}
      </button>

      {isOpen ? (
        <ShareModal onClickClose={close} />
      ) : null}
    </>
  )
}
ShareButton.propTypes = {
  children: PropTypes.node.isRequired // contents of the button
}

export default withI18n()(ShareButton)
