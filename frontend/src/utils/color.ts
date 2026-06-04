export function getContrastColors(hexColor: string) {
  const hex = hexColor.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)

  const luminance = 0.299 * r + 0.587 * g + 0.114 * b

  if (luminance > 150) {
    return {
      text: '#1a1a1a',
      textMuted: 'rgba(0, 0, 0, 0.6)',
      iconFilter: 'brightness(0)'
    }
  }

  return {
    text: '#ffffff',
    textMuted: 'rgba(255, 255, 255, 0.7)',
    iconFilter: 'brightness(0) invert(1)'
  }
}
