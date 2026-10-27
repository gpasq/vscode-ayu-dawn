import { writeFileSync } from 'fs'
import { join } from 'path'
import template, { SchemeName } from './template'
import iconTemplate from './icon-template'

const cwd = process.cwd()

// Generate color themes
for (const variant of ['light', 'mirage'] as SchemeName[]) {
  writeFileSync(
    join(cwd, `ayu-dawn-${variant}.json`),
    JSON.stringify(template(variant, true), null, '\t')
  )
  writeFileSync(
    join(cwd, `ayu-dawn-${variant}-unbordered.json`),
    JSON.stringify(template(variant, false), null, '\t')
  )
  console.log(`Updated ${variant}`)
}

// Generate icon theme
writeFileSync(join(cwd, 'ayu-dawn-icons.json'), JSON.stringify(iconTemplate(), null, '\t'))
console.log('Updated icon theme')
