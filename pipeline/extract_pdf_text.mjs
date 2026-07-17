#!/usr/bin/env node
import fs from 'node:fs/promises'
import path from 'node:path'
import { createHash } from 'node:crypto'
import * as pdfjsLib from '../app/node_modules/pdfjs-dist/legacy/build/pdf.mjs'

const root = path.resolve(new URL('..', import.meta.url).pathname)
const cacheDir = path.join(root, 'data/.cache/pdf')

function usage() {
  console.error('usage: node pipeline/extract_pdf_text.mjs <county-id>')
  process.exit(2)
}

const county = process.argv[2]
if (!county) usage()

const countyRoot = path.join(root, 'data/washington-state/counties', county)
const outDir = path.join(countyRoot, 'interim/pdf-text')

async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true })
  const files = []
  for (const entry of entries) {
    const p = path.join(dir, entry.name)
    if (entry.isDirectory()) files.push(...await walk(p))
    else if (entry.name.endsWith('.pdf.url')) files.push(p)
  }
  return files
}

function slugFromPointer(file) {
  return path.basename(file, '.pdf.url')
}

async function download(url) {
  await fs.mkdir(cacheDir, { recursive: true })
  const key = createHash('sha256').update(url).digest('hex').slice(0, 24)
  const cachePath = path.join(cacheDir, `${key}.pdf`)
  try {
    await fs.access(cachePath)
    return cachePath
  } catch {}
  const res = await fetch(url, {
    headers: {
      accept: 'application/pdf,application/octet-stream,*/*',
      'accept-language': 'en-US,en;q=0.9',
      'user-agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36',
    },
  })
  if (!res.ok) throw new Error(`download failed ${res.status}: ${url}`)
  const bytes = new Uint8Array(await res.arrayBuffer())
  await fs.writeFile(cachePath, bytes)
  return cachePath
}

async function extract(pdfPath) {
  const bytes = await fs.readFile(pdfPath)
  const doc = await pdfjsLib.getDocument({ data: new Uint8Array(bytes), disableWorker: true }).promise
  const pages = []
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i)
    const content = await page.getTextContent()
    const text = content.items
      .map((item) => item.str)
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim()
    pages.push(`--- page ${i} ---\n${text}`)
  }
  return pages.join('\n\n')
}

await fs.mkdir(outDir, { recursive: true })
const pointers = await walk(path.join(countyRoot, 'raw'))
if (!pointers.length) {
  console.error(`no .pdf.url files found for ${county}`)
  process.exit(1)
}

const manifest = []
for (const pointer of pointers) {
  const url = (await fs.readFile(pointer, 'utf8')).trim()
  const slug = slugFromPointer(pointer)
  let cachePath
  try {
    cachePath = await download(url)
  } catch (err) {
    console.warn(`${county}: skipped ${slug}: ${err.message}`)
    manifest.push({
      source_pointer: path.relative(root, pointer),
      url,
      error: err.message,
    })
    continue
  }
  const text = await extract(cachePath)
  const outPath = path.join(outDir, `${slug}.txt`)
  await fs.writeFile(outPath, `${text}\n`)
  manifest.push({
    source_pointer: path.relative(root, pointer),
    url,
    output: path.relative(root, outPath),
  })
  console.log(`${county}: extracted ${slug}`)
}

await fs.writeFile(
  path.join(outDir, 'manifest.json'),
  JSON.stringify({ county, script: 'pipeline/extract_pdf_text.mjs', files: manifest }, null, 2)
)
