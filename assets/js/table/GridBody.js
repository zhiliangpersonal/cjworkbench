import React from 'react'
import PropTypes from 'prop-types'
import memoize from 'memoize-one'
import GridTile from './GridTile'

export default class GridBody extends React.PureComponent {
  static propTypes = {
    nRows: PropTypes.number.isRequired,
    nRowsPerTile: PropTypes.number.isRequired,
    nColumnsPerTile: PropTypes.number.isRequired,
    columns: PropTypes.arrayOf(PropTypes.shape({
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      width: PropTypes.number.isRequired,
      isSelected: PropTypes.bool.isRequired
    })).isRequired,
    // tiles[1][2][3][4] is value at row=(1*200+3), column=(2*50+4)
    tiles: PropTypes.arrayOf(
      PropTypes.arrayOf(
        PropTypes.arrayOf(
          PropTypes.array.isRequired
        ).isRequired
      ).isRequired
    ).isRequired,
    onScroll: PropTypes.func.isRequired, // func({ minTileRow, minTileColumn, maxTileRow, maxTileColumn }) => undefined
  }

  getColumnTiles = memoize((columns, nColumnsPerTile) => {
    const columnTiles = []

    for (let i = 0; i < columns.length; i += nColumnsPerTile) {
      columnTiles.push(columns.slice(i, i + nColumnsPerTile))
    }

    return columnTiles
  })

  render () {
    const { columns, nColumnsPerTile, tiles } = this.props
    const columnTiles = this.getColumnTiles(columns, nColumnsPerTile)

    return (
      <tbody>
        {tiles.map((rowTile, rowTileIndex) => (
          <tr key={rowTileIndex} className='tile-row'>
            {rowTile.map((tile, i) => (
              <td key={i} colSpan={columnTiles[i].length} className='tile'>
                <GridTile
                  addRowNumbers={i === 0}
                  columns={this.getColumnTiles(columns, nColumnsPerTile)[i]}
                  rows={tile}
                />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    )
  }
}
