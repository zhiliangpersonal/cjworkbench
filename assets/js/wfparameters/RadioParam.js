// Simple wrapper over HTML <select>
import React from 'react'
import PropTypes from 'prop-types'

export default class RadioParam extends React.PureComponent {
  static propTypes = {
    name: PropTypes.string.isRequired,
    items: PropTypes.string.isRequired,  // like 'Apple|Banana|Kitten'
    selectedIdx: PropTypes.number.isRequired,
    isReadOnly: PropTypes.bool.isRequired,
    onChange: PropTypes.func.isRequired // called with index of selected item
  }

  onChange = (ev) => {
    this.props.onChange(+ev.target.value)
  }

  render() {
    const { items, isReadOnly, selectedIdx } = this.props
    const itemDivs = items.split('|').map((name, idx) => {
      return (
        <label key={idx} className='t-d-gray content-1'>
          <input
            className='radio-button'
            type='radio'
            value={String(idx)}
            checked={idx === selectedIdx}
            onChange={this.onChange}
            disabled={this.props.isReadOnly}
          />
          <span className="button"></span>
          {name}
        </label>
      )
    })

    return (
      <div className='button-group'>
        {itemDivs}
      </div>
    )
  }
}
