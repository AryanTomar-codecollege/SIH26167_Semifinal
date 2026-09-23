import { useMemo, useState } from 'react'
import { Activity, ChevronDown, CircleHelp, Download, FileText, Layers3, Loader2, MapPinned, Menu, MessageSquare, PanelRight, Play, RotateCcw, Satellite, Send, ShieldCheck, SlidersHorizontal, Sparkles, UploadCloud, X } from 'lucide-react'
import UploadCard from './components/UploadCard'
import MapView from './components/MapView'
import { submitQuery } from './lib/api'

const modes = [
  { id: 'single', label: 'Single image', sub: 'VQA / caption / grounding' },
  { id: 'temporal', label: 'Before / After', sub: 'Bi-temporal change' },
  { id: 'sar', label: 'Optical + SAR', sub: 'Cross-modal analysis' },
]

const examples = [
  'What is visible in this image?',
  'Highlight the buildings in this region.',
  'What changed between Before and After?',
  'Use both images to assess built-up and water areas.',
]

function normalizeGeoJson(value) {
  if (!value) return null
  if (typeof value === 'object') return value
  try { return JSON.parse(value) } catch { return null }
}

function StatusDot({ online = true }) {
  return <span className={`inline-block h-1.5 w-1.5 rounded-full ${online ? 'bg-[#91a78f]' : 'bg-[#9b776e]'}`} />
}

function Trace({ trace }) {
  const [open, setOpen] = useState(false)
  if (!trace) return null
  const items = Array.isArray(trace) ? trace : Object.entries(trace).map(([key, value]) => ({ key, value }))
  return (
    <div className="border-t border-[#2b353a] pt-3">
      <button onClick={() => setOpen(!open)} className="flex w-full items-center justify-between text-left">
        <div>
          <div className="text-[11px] font-semibold text-[#dbe1e2]">Execution trace</div>
          <div className="mt-0.5 text-[9px] text-[#738086]">Observable task and tool summary</div>
        </div>
        <ChevronDown size={14} className={`text-[#778389] transition ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="mt-2 space-y-1.5">
          {items.map((item, index) => (
            <div key={index} className="grid grid-cols-[76px_1fr] gap-2 rounded bg-[#10171b] px-2.5 py-2 text-[9px]">
              <span className="uppercase tracking-wide text-[#69767b]">{item.key || item.step || 'step'}</span>
              <span className="text-[#aeb8bb]">{typeof item.value === 'object' ? JSON.stringify(item.value) : String(item.value ?? item)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [mode, setMode] = useState('single')
  const [files, setFiles] = useState({ primary: null, secondary: null })
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const canRun = useMemo(() => {
    if (!query.trim() || !files.primary) return false
    if (mode !== 'single' && !files.secondary) return false
    return true
  }, [query, files, mode])

  function setModeSafe(next) {
    setMode(next)
    setResult(null)
    setError('')
  }

  function clearAll() {
    setFiles({ primary: null, secondary: null })
    setQuery('')
    setResult(null)
    setMessages([])
    setError('')
  }

  async function runQuery(text = query) {
    if (!text.trim()) return
    if (!files.primary) {
      setError('Add a source image before running an analysis.')
      return
    }
    if (mode !== 'single' && !files.secondary) {
      setError('This workflow needs both image inputs.')
      return
    }

    setLoading(true)
    setError('')
    setMessages((current) => [...current, { role: 'user', text }])
    try {
      const payloadFiles = [{ file: files.primary, role: mode === 'temporal' ? 'before' : mode === 'sar' ? 'optical' : 'primary' }]
      if (files.secondary) payloadFiles.push({ file: files.secondary, role: mode === 'temporal' ? 'after' : 'sar' })
      const data = await submitQuery({ files: payloadFiles, query: text })
      setResult(data)
      setMessages((current) => [...current, { role: 'assistant', text: data.answer || 'Analysis completed.' }])
    } catch (err) {
      setError(err.message || 'The analysis request failed.')
      setMessages((current) => [...current, { role: 'assistant', text: 'I could not complete the analysis. Check the backend connection and try again.' }])
    } finally {
      setLoading(false)
    }
  }

  const geojson = normalizeGeoJson(result?.geojson)
  const confidence = result?.confidence
  const task = result?.task || result?.metadata?.task || 'Awaiting analysis'
  const model = result?.model || result?.metadata?.model || '—'

  return (
    <div className="min-h-screen bg-[#0d1317] text-[#e7ecee]">
      <header className="flex h-16 items-center justify-between border-b border-[#273137] bg-[#10171b] px-5">
        <div className="flex items-center gap-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-md border border-[#3b484d] bg-[#182024]"><Satellite size={18} /></div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold tracking-[0.04em]">SATQUERY AI</span>
              <span className="rounded border border-[#344047] px-1.5 py-0.5 text-[8px] font-semibold tracking-[0.14em] text-[#879399]">SIH 26167</span>
            </div>
            <div className="mt-0.5 text-[9px] uppercase tracking-[0.14em] text-[#69767b]">Interactive remote-sensing analysis</div>
          </div>
        </div>

        <div className="hidden items-center gap-6 text-[9px] uppercase tracking-[0.12em] text-[#7f8b90] md:flex">
          <span className="flex items-center gap-2"><StatusDot /> Local API ready</span>
          <span className="flex items-center gap-2"><StatusDot /> GIS engine ready</span>
          <span className="flex items-center gap-2"><StatusDot online={false} /> GPU session on demand</span>
        </div>

        <button onClick={clearAll} className="rounded-md border border-[#303b40] bg-[#151d21] p-2 text-[#9aa5a9] hover:text-[#e4e9ea]" title="Reset workspace">
          <RotateCcw size={15} />
        </button>
      </header>

      <div className="grid h-[calc(100vh-4rem)] grid-cols-[285px_minmax(420px,1fr)_390px]">
        <aside className="thin-scroll overflow-y-auto border-r border-[#273137] bg-[#11181c] p-4">
          <div className="mb-4 flex items-center justify-between">
            <div><div className="eyebrow">Analysis workspace</div><div className="mt-1 text-xs text-[#cbd2d4]">Choose an input workflow</div></div>
            <SlidersHorizontal size={15} className="text-[#68757a]" />
          </div>

          <div className="space-y-1 rounded-lg border border-[#2a3439] bg-[#0e1519] p-1">
            {modes.map((item) => (
              <button key={item.id} onClick={() => setModeSafe(item.id)} className={`w-full rounded-md px-2.5 py-2 text-left transition ${mode === item.id ? 'bg-[#202b2d] text-[#e8eeee]' : 'text-[#8e9a9f] hover:bg-[#172025]'}`}>
                <div className="text-[11px] font-medium">{item.label}</div>
                <div className="mt-0.5 text-[9px] text-[#6e7a7f]">{item.sub}</div>
              </button>
            ))}
          </div>

          <div className="mt-5 space-y-2">
            <UploadCard label={mode === 'temporal' ? 'Before image' : mode === 'sar' ? 'Optical image' : 'Source image'} hint="GeoTIFF / TIFF · georeferenced source" file={files.primary} onFile={(file) => setFiles((f) => ({ ...f, primary: file }))} onRemove={() => setFiles((f) => ({ ...f, primary: null }))} />
            {mode !== 'single' && <UploadCard label={mode === 'temporal' ? 'After image' : 'SAR image'} hint="Paired input · co-registration checked by backend" file={files.secondary} onFile={(file) => setFiles((f) => ({ ...f, secondary: file }))} onRemove={() => setFiles((f) => ({ ...f, secondary: null }))} />}
          </div>

          <div className="mt-5 rounded-lg border border-[#2b353a] bg-[#151d21] p-3">
            <div className="flex items-center gap-2"><ShieldCheck size={14} className="text-[#91a78f]" /><span className="text-[10px] font-semibold text-[#cfd6d7]">Input gate</span></div>
            <div className="mt-2 space-y-1.5 text-[9px] text-[#7e8a8f]">
              <div className="flex justify-between"><span>Format</span><span className={files.primary ? 'text-[#9eaca4]' : ''}>{files.primary ? 'selected' : 'waiting'}</span></div>
              <div className="flex justify-between"><span>Modality</span><span>{mode === 'sar' ? 'optical + SAR' : mode === 'temporal' ? 'before + after' : 'single'}</span></div>
              <div className="flex justify-between"><span>CRS / bands</span><span>backend check</span></div>
            </div>
          </div>

          <div className="mt-5 text-[9px] leading-4 text-[#68757a]">
            Original imagery remains the geospatial source of truth. The interface only previews working representations; CRS and transform decisions belong to the backend.
          </div>
        </aside>

        <main className="relative min-w-0 bg-[#d8ddda]">
          <div className="absolute left-4 top-4 z-[500] flex items-center gap-2 rounded-md border border-[#344047] bg-[#11181c]/95 px-3 py-2 shadow-lg">
            <MapPinned size={14} className="text-[#a5b0b2]" />
            <span className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#cdd4d5]">Evidence map</span>
            <span className="text-[9px] text-[#6f7c81]">{geojson ? 'GeoJSON layer active' : 'No evidence yet'}</span>
          </div>
          <div className="absolute right-4 top-4 z-[500] flex overflow-hidden rounded-md border border-[#344047] bg-[#11181c]/95 shadow-lg">
            <button className="px-2.5 py-2 text-[#aab4b6] hover:bg-[#1d272c]"><Layers3 size={14} /></button>
            <button className="border-l border-[#344047] px-2.5 py-2 text-[#aab4b6] hover:bg-[#1d272c]"><PanelRight size={14} /></button>
          </div>
          <MapView geojson={geojson} />
          {!geojson && !files.primary && (
            <div className="pointer-events-none absolute inset-0 z-[400] flex items-center justify-center">
              <div className="rounded-xl border border-[#3a454a] bg-[#10171b]/90 px-7 py-6 text-center shadow-2xl">
                <MapPinned size={22} className="mx-auto mb-3 text-[#8a9895]" />
                <div className="text-sm font-medium text-[#dfe5e5]">Your analysis map</div>
                <div className="mt-1 max-w-xs text-[10px] leading-4 text-[#7a878c]">Upload a georeferenced image, ask a question, and spatial evidence will appear here.</div>
              </div>
            </div>
          )}
        </main>

        <aside className="thin-scroll flex min-h-0 flex-col border-l border-[#273137] bg-[#11181c]">
          <div className="border-b border-[#273137] px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2"><MessageSquare size={14} className="text-[#9aa5a9]" /><span className="text-xs font-semibold">Ask SatQuery</span></div>
              <span className="text-[9px] text-[#6f7b80]">Natural language</span>
            </div>
          </div>

          <div className="thin-scroll min-h-0 flex-1 overflow-y-auto px-4 py-4">
            {messages.length === 0 ? (
              <div className="rounded-lg border border-[#2c373c] bg-[#151d21] p-4">
                <div className="flex items-start gap-2"><Sparkles size={14} className="mt-0.5 text-[#9aa8a1]" /><div><div className="text-[11px] font-medium text-[#d7dede]">Start with a task</div><div className="mt-1 text-[9px] leading-4 text-[#748187]">The controller routes metadata locally and sends visual tasks to the registered EarthDial workflow.</div></div></div>
                <div className="mt-4 space-y-1.5">
                  {examples.map((example) => <button key={example} onClick={() => setQuery(example)} className="w-full rounded-md border border-[#303b40] bg-[#10171b] px-2.5 py-2 text-left text-[9px] text-[#9ba6a9] hover:border-[#4a575b] hover:text-[#d4dbdc]">{example}</button>)}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((message, i) => (
                  <div key={i} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[88%] rounded-lg px-3 py-2.5 text-[10px] leading-4 ${message.role === 'user' ? 'bg-[#263238] text-[#dce3e4]' : 'border border-[#2d383d] bg-[#171f23] text-[#aeb8bb]'}`}>{message.text}</div>
                  </div>
                ))}
                {loading && <div className="flex items-center gap-2 text-[9px] text-[#7c898e]"><Loader2 size={13} className="animate-spin" /> Running registered analysis workflow…</div>}
              </div>
            )}

            {error && <div className="mt-3 flex gap-2 rounded-md border border-[#5a423d] bg-[#251b19] p-2.5 text-[9px] leading-4 text-[#c9a49a]"><CircleHelp size={13} className="mt-0.5 shrink-0" />{error}</div>}

            {result && (
              <div className="mt-4 rounded-lg border border-[#33403f] bg-[#151d21] p-3.5">
                <div className="flex items-center justify-between"><span className="eyebrow">Analysis result</span><span className="rounded border border-[#36423f] bg-[#1a2421] px-1.5 py-0.5 text-[8px] uppercase tracking-wide text-[#9eaca4]">{task}</span></div>
                <div className="mt-3 text-[11px] leading-5 text-[#d7ddde]">{result.answer || 'No answer returned.'}</div>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <div className="rounded-md bg-[#10171b] p-2.5"><div className="text-[8px] uppercase tracking-wide text-[#667379]">Confidence</div><div className="mt-1 text-xs font-semibold text-[#bdc8c8]">{confidence ?? '—'}{typeof confidence === 'number' && confidence <= 1 ? '' : ''}</div></div>
                  <div className="rounded-md bg-[#10171b] p-2.5"><div className="text-[8px] uppercase tracking-wide text-[#667379]">Model</div><div className="mt-1 truncate text-[9px] font-medium text-[#aeb8bb]">{model}</div></div>
                </div>
                {result.warnings?.length > 0 && <div className="mt-3 rounded-md border border-[#4a4031] bg-[#221e16] p-2 text-[9px] text-[#b8aa8d]">{result.warnings.join(' ')}</div>}
                <div className="mt-4"><Trace trace={result.execution_trace || result.trace} /></div>
              </div>
            )}
          </div>

          <div className="border-t border-[#273137] p-3">
            <div className="rounded-lg border border-[#303b40] bg-[#0f161a] focus-within:border-[#56635e]">
              <textarea value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); runQuery() } }} placeholder="Ask about the image…" className="h-20 w-full resize-none bg-transparent px-3 py-2.5 text-[10px] leading-4 text-[#dce2e3] outline-none placeholder:text-[#5f6b70]" />
              <div className="flex items-center justify-between border-t border-[#293338] px-2 py-2">
                <span className="pl-1 text-[8px] text-[#5d696e]">Enter to run · Shift+Enter for new line</span>
                <button disabled={!canRun || loading} onClick={() => runQuery()} className="flex items-center gap-1.5 rounded-md border border-[#3b4845] bg-[#27332f] px-2.5 py-1.5 text-[9px] font-semibold text-[#d5dcda] disabled:cursor-not-allowed disabled:opacity-40"><Send size={12} /> Analyze</button>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
