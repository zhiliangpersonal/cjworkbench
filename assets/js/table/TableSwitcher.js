import React from 'react'
import PropTypes from 'prop-types'
import LoadingTable from './LoadingTable'

function areSameTable(props1, props2) {
  if (props1 === null && props2 === null) return true // both null => true
  if ((props1 === null) !== (props2 === null)) return false // one null => false

  return props1.wfModuleId === props2.wfModuleId
    && props1.deltaId === props2.deltaId
    && props1.nRows === props2.nRows
}

/**
 * Shows a <LoadingTable> for the given wfModule+deltaId -- and transitions
 * when those props change.
 *
 * The transition is: this.state maintains a "last-loaded" wfModule+deltaId.
 * When we switch to a new wfModule+deltaId that has not yet loaded (or has
 * nRows===null), we keep that stale table visible atop the new, unloaded one
 * and we show a spinner.
 *
 *   <div className="table-switcher">
 *     <div className="loaded-table">
 *       <LoadingTable ... /> <!-- last table we've seen with data -->
 *     </div>
 *     <div className="loading-table">
 *       <LoadingTable ... /> <!-- next table -- when it loads, we'll move it -->
 *       <Spinner ... />
 *     </div>
 *   </div>
 */
export default class TableSwitcher extends React.PureComponent {
  static propTypes = {
    wfModuleId: PropTypes.number,
    deltaId: PropTypes.number,
    nRows: PropTypes.number, // or null, if status!=ok
    columns: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string.isRequired,
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      width: PropTypes.number.isRequired,
      isSelected: PropTypes.bool.isRequired
    })).isRequired,
    nRowsPerTile: PropTypes.number.isRequired,
    nColumnsPerTile: PropTypes.number.isRequired,
    loadTile: PropTypes.func.isRequired // func(wfModuleId, deltaId, tileRow, tileColumn) => Promise[Array[Array]]
  }

  state = {
    loaded: null // { wfModuleId, deltaId, nRows, columns } of a table that has rendered something, sometime
  }

  /**
   * Render a <LoadingTable>, with a `key` tied to wfModuleId+deltaId so tables
   * are guaranteed to never share data.
   */
  _renderTable (props, className) {
    const { wfModuleId, deltaId, nRows, columns } = props
    const { nRowsPerTile, nColumnsPerTile, loadTile } = this.props

    return (
      <div key={`${wfModuleId}-${deltaId}`} className={className}>
        <LoadingTable
          wfModuleId={wfModuleId}
          deltaId={deltaId}
          nRows={nRows}
          columns={columns}
          nRowsPerTile={nRowsPerTile}
          nColumnsPerTile={nColumnsPerTile}
          loadTile={loadTile}
          onLoadTile={this.onLoadTile}
        />
        {className === 'loaded-table' ? null : (
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

  onLoadTile = (wfModuleId, deltaId) => {
    const loaded = this.state.loaded

    if (wfModuleId !== this.props.wfModuleId || deltaId !== this.props.deltaId) {
      return // Spurious request -- we aren't rendering this table
    }

    if (areSameTable(this.props, loaded)) {
      return // We already received a tile for this table, so no state change can happen
    }

    // Now 
    const { nRows, columns } = this.props

    this.setState({
      loaded: { wfModuleId, deltaId, nRows, columns }
    })
  }

  render () {
    const { loaded } = this.state

    const tables = []

    if (loaded) {
      tables.push(this._renderTable(loaded, 'loaded-table'))
    }

    if (this.props.nRows !== null && !areSameTable(this.props, loaded)) {
      tables.push(this._renderTable(this.props, 'loading-table'))
    }

    if (loaded === null && this.props.nRows === null) {
      tables.push(<div className='placeholder-table'>TODO empty table here</div>)
    }

    return (
      <div className='table-switcher'>
        {tables}
      </div>
    )
  }
}
