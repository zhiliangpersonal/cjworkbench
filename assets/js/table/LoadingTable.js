import React from 'react'
import PropTypes from 'prop-types'
import Grid from './Grid'


function buildTileArray(nRows, nRowsPerTile, nColumns, nColumnsPerTile) {
  const nRowTiles = Math.ceil(nRows / nRowsPerTile)
  const nColumnTiles = Math.ceil(nColumns / nColumnsPerTile)

  const oneRow = []
  for (let i = 0; i < nColumnTiles; i++) {
    oneRow.push(null)
  }

  const rows = []
  for (let i = 0; i < nRowTiles; i++) {
    rows.push(oneRow)
  }

  return rows
}

/**
 * Wrapper for <Table> that loads data.
 *
 * Assumes the WfModule's status is 'ok'. The caller can pass `onLoadTile` to
 * detect when data has loaded.
 */
export default class LoadingTable extends React.PureComponent {
  static propTypes = {
    wfModuleId: PropTypes.number.isRequired,
    deltaId: PropTypes.number.isRequired,
    columns: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string.isRequired,
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      width: PropTypes.number.isRequired,
      isSelected: PropTypes.bool.isRequired
    })).isRequired,
    nRows: PropTypes.number.isRequired,
    nRowsPerTile: PropTypes.number.isRequired,
    nColumnsPerTile: PropTypes.number.isRequired,
    loadTile: PropTypes.func.isRequired, // func(wfModuleId, deltaId, tileRow, tileColumn) => Promise[Array[Array]]
    onLoadTile: PropTypes.func.isRequired // func(wfModuleId, deltaId, tileRow, tileColumn) => undefined
  }

  state = {
    tiles: buildTileArray(
      this.props.nRows,
      this.props.nRowsPerTile,
      this.props.columns.length,
      this.props.nColumnsPerTile
    ),
    loading: [] // Tiles queued for load
  }

  mounted = true

  componentWillUnmount () {
    this.mounted = false
  }

  componentDidMount () {
    this.startLoadTile(0, 0)
  }

  startLoadTile (tileRow, tileColumn) {
    const { wfModuleId, deltaId } = this.props
    this.props.loadTile(wfModuleId, deltaId, tileRow, tileColumn)
      .then(rows => {
        if (!this.mounted) return

        this.setState(state => {
          // Add a tile
          const tiles = state.tiles.slice()
          tiles[tileRow] = state.tiles[tileRow].slice()
          tiles[tileRow][tileColumn] = rows

          // Remove from loading
          const loading = state.loading.slice()
          loading.splice(loading.indexOf(`${tileRow},${tileColumn}`), 1)

          return { tiles, loading }
        })

        this.props.onLoadTile(wfModuleId, deltaId, tileRow, tileColumn)
      })
  }

  onScroll = (minTileRow, minTileColumn, maxTileRow, maxTileColumn) => {
    const tiles = this.state.tiles

    for (let i = minTileRow; i <= maxTileRow; i++) {
      for (let j = minTileColumn; j <= maxTileColumn; j++) {
        if (this.tiles[i][j] === null && !this.loading.includes(`${i},${j}`)) {
          this.startLoadTile(i, j)
        }
      }
    }
  }

  render () {
    const { columns, nRows, nRowsPerTile, nColumnsPerTile, onScroll } = this.props
    const { tiles, loading } = this.state

    return (
      <div className="table-loader">
        <Grid
          columns={columns}
          nRows={nRows}
          nRowsPerTile={nRowsPerTile}
          nColumnsPerTile={nColumnsPerTile}
          tiles={tiles}
          onScroll={onScroll}
        />
        {loading.length === 0 ? null : (
          <div id="spinner-container-transparent">
            <div id="spinner-l1">
              <div id="spinner-l2">
                <div id="spinner-l3"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }
}
