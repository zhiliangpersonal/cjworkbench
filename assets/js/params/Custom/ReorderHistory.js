import React from 'react'
import PropTypes from 'prop-types'
import { idxToLetter } from '../../utils'
import { withJsonStringValues } from '../util'
import { Trans,t } from '@lingui/macro'
import { withI18n,I18n } from '@lingui/react'

export class ReorderHistory extends React.Component {
  static propTypes = {
    value: PropTypes.arrayOf(PropTypes.shape({
      column: PropTypes.string.isRequired,
      from: PropTypes.number.isRequired,
      to: PropTypes.number.isRequired
    }).isRequired).isRequired
  }

  render () {
    const { value } = this.props

    return (
      <table className='table'>
        <thead>
          <tr>
            <td className='reorder-info'>#</td>
            <td className='reorder-info'><Trans id="reorderHistory.column">COLUMN</Trans></td>
            <td className='reorder-position'><Trans id="reorderHistory.from">FROM</Trans></td>
            <td className='reorder-position'><Trans id="reorderHistory.to">TO</Trans></td>
          </tr>
        </thead>
        <tbody>
          {value.map(({ column, from, to }, idx) => (
            <tr key={idx}>
              <td className='reorder-idx'>{idx + 1}</td>
              <td className='reorder-column'>{column}</td>
              <td className='reorder-from'>{idxToLetter(from)}</td>
              <td className='reorder-to'>{idxToLetter(to)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    )
  }
}

export default withJsonStringValues(ReorderHistory, [])
