import React from 'react'
import PropTypes from 'prop-types'

export class ColumnHeader extends React.PureComponent {
  static propTypes = {
    name: PropTypes.string.isRequired,
    type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
    width: PropTypes.number.isRequired,
    isSelected: PropTypes.bool.isRequired
  }

  render () {
    const { name, type, width, isSelected } = this.props

    return (
      <th style={{width: `${width}px`}}>
        <div className="name">{name}</div>
        <div className="type">{type}</div>
      </th>
    )
  }
}

/**
 * <thead> element with all <ColumnHeader>s inside it.
 *
 * The header isn't tiled because we load all columns ahead of time. We optimize
 * for table-layout:fixed, though. We set the width of each column in the header
 * here; and then when we render a tile (which is a sub-<table>) we give its
 * enclosing <td> a colspan to grab the right width.
 */
export default class GridHead extends React.PureComponent {
  static propTypes = {
    columns: PropTypes.arrayOf(PropTypes.shape({
      index: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      type: PropTypes.oneOf([ 'text', 'datetime', 'number' ]).isRequired,
      width: PropTypes.number.isRequired,
      isSelected: PropTypes.bool.isRequired,
    })).isRequired
  }

  render () {
    const { columns } = this.props

    return (
      <thead>
        <tr>
          {columns.map(c => <ColumnHeader key={c.index} {...c} />)}
        </tr>
      </thead>
    )
  }
}
