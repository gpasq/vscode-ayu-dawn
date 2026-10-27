import { readFileSync } from 'fs'
import { join } from 'path'
import { parse as parseYaml } from 'yaml'
import { Color } from './color'
import { loadColors } from './yaml-parser'
import type { Scheme } from './scheme'

export { Color }
export type { Scheme }

const colorsDir = join(__dirname, '..', '..', 'colors')

// Settle each color to its final hex, so modifiers applied by the template start from the
// resolved value rather than stacking on the YAML's own modifiers
const bake = (value: unknown): unknown => {
  if (value instanceof Color) return new Color(value.hex().slice(1))
  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>).map(([key, v]) => [key, bake(v)])
  )
}

const loadScheme = (name: string) =>
  bake(loadColors<Scheme>(join(colorsDir, `${name}.yaml`))) as Scheme

export const light = loadScheme('light')
export const mirage = loadScheme('mirage')

type IconFile = string | { dark: string; light: string }

export interface Icons {
  default: string
  folder: Record<'dark' | 'light', { collapsed: string; expanded: string }>
  files: Record<string, IconFile>
  extensions: Record<string, string>
  filenames: Record<string, string>
}

export const icons = parseYaml(readFileSync(join(colorsDir, 'icons.yaml'), 'utf-8')) as Icons
