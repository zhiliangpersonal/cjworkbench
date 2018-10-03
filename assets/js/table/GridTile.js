import React from 'react'
import PropTypes from 'prop-types'
import GridRow from './GridRow'

export default class GridTile extends React.PureComponent {
  static propTypes = {
    columns: PropTypes.arrayOf(PropTypes.shape({
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      width: PropTypes.number.isRequired,
      isSelected: PropTypes.bool.isRequired
    })).isRequired,
    rows: PropTypes.arrayOf(PropTypes.array.isRequired).isRequired
  }

  render () {
    const { columns, rows } = this.props

    if (rows === null) return null

    return (
      <table className='tile'>
        {columns.map(c => (
          <col style={{width: `${c.width}px`}} />
        ))}
        {rows.map(values => (
          <GridRow columns={columns} values={values} />
        ))}
      </table>
    )
  }
}
