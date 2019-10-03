// ---- Utilities ---
import * as Cookies from 'js-cookie'
import { fromByteArray as base64Encode } from 'base64-js'
import { t } from '@lingui/macro'

export function goToUrl (url) {
  window.location.href = url
}

// Current CSRF token
export const csrfToken = Cookies.get('csrftoken')

// Gets the letter coordinate of a column from its index within the column names array
export function idxToLetter (idx) {
  var letters = ''
  var cidx = parseInt(idx)
  cidx += 1
  do {
    cidx -= 1
    letters = String.fromCharCode(cidx % 26 + 65) + letters
    cidx = Math.floor(cidx / 26)
  } while (cidx > 0)
  return letters
}

// Log to Intercom, if installed
export function logUserEvent (name, metadata) {
  if (!window.APP_ID) return

  // If we're in a lesson, drop the event.
  if (window.initState && window.initState.lessonData) return

  window.Intercom('trackEvent', name, metadata)
}

export function timeDifference (start, end, i18n) {
  const ms = new Date(end) - new Date(start)
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const years = Math.floor(days / 365.25)

  if (years > 0) {
    return i18n._(t('time_diff.ago.years')`${years}y ago`)
  } else if (days > 0) {
    return i18n._(t('time_diff.ago.days')`${days}d ago`)
  } else if (hours > 0) {
    return i18n._(t('time_diff.ago.hours')`${hours}h ago`)
  } else if (minutes > 0) {
    return i18n._(t('time_diff.ago.minutes')`${minutes}m ago`)
  } else if (seconds > 0) {
    return i18n._(t('time_diff.ago.seconds')`${seconds}s ago`)
  } else {
    return i18n._(t('time_diff.now')`just now`)
  }
}

export function escapeHtml (str) {
  str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')

  return str
}

/**
 * Scroll `containerEl` vertically by the smallest amount possible to put
 * `el` in view.
 *
 * Set the container CSS `scroll-behavior: smooth` to make this transition
 * look nice.
 *
 * @param el Element we want to focus
 * @param containerEl Element we'll set scrollTop on so it contains el
 * @param marginTop Minimum number of pixels between containerEl.top and el.top
 * @param marginBottom Minimum number of pixels between containerEl.bottom and el.bottom
 */
export function scrollTo (el, containerEl, marginTop, marginBottom) {
  if (marginTop === undefined) marginTop = 10
  if (marginBottom === undefined) marginBottom = 10

  const elRect = el.getBoundingClientRect()
  const containerRect = containerEl.getBoundingClientRect()

  // Calculate dy: how much do we need to add to containerEl.scrollTop to
  // make el go where we want it to go?
  let dy = 0 // Prefer not to scroll
  if (elRect.bottom + marginBottom > containerRect.bottom) {
    // Scroll down if we need to.
    // We do this before up because some els might be taller than containerEl,
    // and in that case we want scroll-up to override scroll-down (because the
    // top of el is more important than the bottom).
    dy += (elRect.bottom + marginBottom - containerRect.bottom)
  }
  if (dy + elRect.top - marginTop < containerRect.top) {
    // Scroll up if we need to.
    dy -= (containerRect.top - (elRect.top - marginTop))
  }

  containerEl.scrollTop += dy
}

/**
 * Build a unique slug with the given prefix.
 *
 * The slug uses randomly-generated bytes: 9 bytes, base64-encoded with
 * '+' and '/' changed to '-' and '_' (to fit a Django "slug" field).
 *
 * Django 'slug' regex: r'^[-a-zA-Z0-9_]+\Z'
 *
 * According to https://en.wikipedia.org/wiki/Birthday_attack, 9 bytes -- 72
 * bits -- means if clients call this 97,000 times, they have a <10^-12 chance
 * of generating a collision within a given Workflow. This should protect even
 * the most click-happy user. (6 bytes would allow 380 before the chance grows
 * higher, and 380 steps is possible.)
 *
 * (Why 9 bytes and not 8? Because base64-encoding gives the same string
 * length. 9 bytes encoded as base64 gives 12 bytes.)
 */
export function generateSlug (prefix) {
  const bytes = new Uint8Array(9)
  window.crypto.getRandomValues(bytes)
  return prefix + (
    base64Encode(bytes)
      .replace(/\+/g, '-')
      .replace(new RegExp('/', 'g'), '_')
  )
}
