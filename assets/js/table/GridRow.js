import React from 'react'
import PropTypes from 'prop-types'
import GridCell from './GridCell'

export default class GridRow extends React.PureComponent {
  static propTypes = {
    index: PropTypes.number.isRequired, // absolute index
    columns: PropTypes.arrayOf(PropTypes.shape({
      index: PropTypes.number.isRequired, // absolute index
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      isSelected: PropTypes.bool.isRequired
    })).isRequired,
    values: PropTypes.array.isRequired
  }

  render () {
    const { index, columns, values } = this.props

    return (
      <tr>
        {columns.map((column, i) => (
          <GridCell
            key={i}
            rowIndex={index}
            columnIndex={columns[i].index}
            type={columns[i].type}
            value={values[i]}
          />
        ))}
      </tr>
    )
  }
}
