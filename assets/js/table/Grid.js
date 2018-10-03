import React from 'react'
import PropTypes from 'prop-types'
import GridHead from './GridHead'
import GridBody from './GridBody'

export default class Grid extends React.PureComponent {
  static propTypes = {
    columns: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string.isRequired,
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      width: PropTypes.number.isRequired,
      isSelected: PropTypes.bool.isRequired
    })).isRequired,
    nRows: PropTypes.number.isRequired,
    nRowsPerTile: PropTypes.number.isRequired,
    nColumnsPerTile: PropTypes.number.isRequired,
    // tiles[1][2][3][4] is value at row=(1*200+3), column=(2*50+4)
    tiles: PropTypes.arrayOf(
      PropTypes.arrayOf(
        PropTypes.arrayOf(
          PropTypes.array.isRequired
        ) // tile may be null
      ).isRequired
    ).isRequired,
    onScroll: PropTypes.func.isRequired, // func({ minTileRow, minTileColumn, maxTileRow, maxTileColumn }) => undefined
  }

  render () {
    const { columns, tiles, nRows, nRowsPerTile, nColumnsPerTile } = this.props

    return (
      <table className="grid">
        <GridHead
          columns={columns}
        />
        <GridBody
          columns={columns}
          tiles={tiles}
          nRows={nRows}
          nRowsPerTile={nRowsPerTile}
          nColumnsPerTile={nColumnsPerTile}
        />
      </table>
    )
  }
}
