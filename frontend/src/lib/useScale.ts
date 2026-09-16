import { useEffect, useState } from 'react'

/**
 * Pixel-perfect scale hook.
 * The app is authored at a fixed 1440×900 artboard; we scale it uniformly to
 * fit the viewport while preserving the exact original pixel metrics.
 */
export function useScale(baseW = 1440, baseH = 900) {
  const [scale, setScale] = useState(1)

  useEffect(() => {
    const update = () => {
      const s = Math.min(window.innerWidth / baseW, window.innerHeight / baseH)
      setScale(s)
    }
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [baseW, baseH])

  return scale
}
