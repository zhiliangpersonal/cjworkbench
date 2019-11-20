import React from 'react'
import PropTypes from 'prop-types'
import { withI18n } from '@lingui/react'

export const messagePropType = PropTypes.oneOfType([PropTypes.string, PropTypes.shape({
  id: PropTypes.string.isRequired, // message key
  arguments: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired
})])

function translate (i18n, message) {
  if (!message || (typeof message) !== 'object') return message
  if (message.id === 'TODO_i18n') {
    return message.arguments.text
  } else {
    return i18n._(message.id, message.arguments)
  }
}

/**
 * Render an I18nMessage, as defined in cjwkernel.types.
 *
 * This renders as text in a React.Fragment
 */
function I18nMessage ({ i18n, message }) {
  return <>{translate(i18n, message)}</>
}

I18nMessage.propTypes = {
  message: messagePropType,
  i18n: PropTypes.shape({
    // i18n object injected by LinguiJS withI18n()
    _: PropTypes.func.isRequired
  }).isRequired
}
export default withI18n()(I18nMessage)
