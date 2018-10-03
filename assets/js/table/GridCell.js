import React from 'react'
import PropTypes from 'prop-types'
import { typeToCellFormatter } from './CellFormatters'

export default class GridCell extends React.PureComponent {
  static propTypes = {
    rowIndex: PropTypes.number.isRequired,
    columnIndex: PropTypes.number.isRequired,
    type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
    value: PropTypes.any // or null
  }

  render () {
    const { type, value } = this.props

    const Formatter = typeToCellFormatter(type)

    return (
      <td>
        <Formatter value={value} />
      </td>
    )
  }
}
