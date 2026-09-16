import type { CSSProperties } from 'react'

interface IconProps {
  size?: number
  style?: CSSProperties
}

const box = (size: number, style?: CSSProperties): CSSProperties => ({
  width: size,
  height: size,
  display: 'block',
  flexShrink: 0,
  ...style,
})

/** Brand mark — open emerald ring (270° arc, gap in the upper-right quadrant)
 *  with a filled centre node. Geometry read pixel-by-pixel from the canvas. */
export function LogoMark({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" style={box(size)}>
      <circle
        cx="10"
        cy="10"
        r="8.5"
        stroke="#34D399"
        strokeWidth="3"
        strokeDasharray="40.06 13.35"
      />
      <circle cx="10" cy="10" r="3" fill="#34D399" />
    </svg>
  )
}

export function PlusIcon({ size = 14, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  )
}

/** Search — ring + handle, matching the canvas geometry. */
export function SearchIcon({ size = 16, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <circle cx="10.7" cy="10.7" r="7" stroke="currentColor" strokeWidth="2" />
      <path d="M20 20l-4.2-4.2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function ChevronDown({ size = 14, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <path d="M6 9.5l6 6 6-6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function CloseIcon({ size = 16, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <path d="M5.5 5.5l13 13M18.5 5.5l-13 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function ArrowUp({ size = 20, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <path d="M12 19.5V5M6 11l6-6 6 6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

/** Chat — speech bubble with a tucked tail, per the canvas channel card. */
export function ChatIcon({ size = 18, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="none" style={box(size, style)}>
      <path
        d="M2.6 4.6c0-1.1.9-2 2-2h8.8c1.1 0 2 .9 2 2v5.6c0 1.1-.9 2-2 2H7.4l-3.4 2.6v-2.6h-.4c-1.1 0-2-.9-2-2V4.6z"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
    </svg>
  )
}

/** Padlock — shackle arc over a rounded body. */
export function LockIcon({ size = 14, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="2" />
      <path d="M8 11V8a4 4 0 018 0v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function FolderIcon({ size = 16, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <path
        d="M3 6.5A1.5 1.5 0 014.5 5h4l1.8 2h9.2A1.5 1.5 0 0121 8.5v9A1.5 1.5 0 0119.5 19h-15A1.5 1.5 0 013 17.5v-11z"
        stroke="currentColor"
        strokeWidth="1.9"
        strokeLinejoin="round"
      />
    </svg>
  )
}

/** 任务看板 — three vertical bars of staggered height. */
export function BoardIcon({ size = 18, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="none" style={box(size, style)}>
      <rect x="2.6" y="3" width="3.75" height="12" rx="1.125" stroke="currentColor" strokeWidth="1.8" />
      <rect x="7.1" y="3" width="3.75" height="8.25" rx="1.125" stroke="currentColor" strokeWidth="1.8" />
      <rect x="11.9" y="3" width="3" height="10.5" rx="1.125" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  )
}

/** 团队资产 — stacked layers. */
export function AssetsIcon({ size = 18, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="none" style={box(size, style)}>
      <path d="M9 2.2l6.4 3.1L9 8.4 2.6 5.3 9 2.2z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M2.6 9.1L9 12.2l6.4-3.1" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M2.6 12.4L9 15.5l6.4-3.1" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
    </svg>
  )
}

/** 控制中心 — two sliders with knobs. */
export function ControlIcon({ size = 18, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="none" style={box(size, style)}>
      <path d="M3 6h12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="7.2" cy="6" r="1.9" stroke="currentColor" strokeWidth="1.7" />
      <path d="M3 12h12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="11.4" cy="12" r="1.9" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  )
}

/** 设置 — gear: ring of teeth around a centre dot. */
export function SettingsIcon({ size = 18, style }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={box(size, style)}>
      <circle cx="12" cy="12" r="3.1" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 2.6l1.7 2.6 3-.7.5 3 2.9 1-1.5 2.6 1.5 2.6-2.9 1-.5 3-3-.7L12 21.4l-1.7-2.6-3 .7-.5-3-2.9-1L5.4 13 3.9 10.4l2.9-1 .5-3 3 .7L12 2.6z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  )
}
