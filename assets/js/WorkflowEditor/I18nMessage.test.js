/* global describe, it, expect */
import React from 'react'
import I18nMessage from './I18nMessage'
import { mountWithI18n } from '../i18n/test-utils'

describe('I18nMessage', () => {
  const wrapper = (message, extraProps = {}) => {
    return mountWithI18n(
      <I18nMessage
        message={message}
        {...extraProps}
      />
    )
  }

  it('should ignore null and undefined', () => {
    expect(wrapper(null).find('I18nMessage').text()).toEqual('')
    expect(wrapper(undefined).find('I18nMessage').text()).toEqual('')
  })

  it('should just output plain strings', () => {
    expect(wrapper('Plain string').find('I18nMessage').text()).toEqual('Plain string')
  })

  it('should support "TODO_i18n" special message id', () => {
    expect(wrapper({ id: 'TODO_i18n', arguments: { text: 'Test me' } }).find('I18nMessage').text()).toEqual('Test me')
  })
})
