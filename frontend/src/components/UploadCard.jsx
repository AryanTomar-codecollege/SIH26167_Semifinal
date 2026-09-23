import { FileUp, X, CheckCircle2 } from 'lucide-react'

export default function UploadCard({ label, hint, file, onFile, onRemove, disabled }) {
  return (
    <div className="rounded-lg border border-[#303b40] bg-[#10171b] p-3">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-[#e8edef]">{label}</div>
          <div className="mt-0.5 text-[10px] text-[#7f8b90]">{hint}</div>
        </div>
        {file && <CheckCircle2 size={15} className="text-[#91a78f]" />}
      </div>

      {!file ? (
        <label className={`flex min-h-20 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-[#3a464b] bg-[#151d21] text-center transition hover:border-[#73847b] ${disabled ? 'pointer-events-none opacity-50' : ''}`}>
          <FileUp size={17} className="mb-1 text-[#9ba6a9]" />
          <span className="text-[11px] text-[#b8c0c3]">Drop GeoTIFF or browse</span>
          <span className="mt-1 text-[9px] text-[#6f7b80]">.tif / .tiff</span>
          <input type="file" accept=".tif,.tiff,image/tiff" className="hidden" onChange={(e) => onFile(e.target.files?.[0] || null)} />
        </label>
      ) : (
        <div className="flex items-center justify-between rounded-md border border-[#34403e] bg-[#19211f] px-2.5 py-2">
          <div className="min-w-0">
            <div className="truncate text-[11px] font-medium text-[#dce2e2]">{file.name}</div>
            <div className="mt-0.5 text-[9px] text-[#7f8b90]">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
          </div>
          <button onClick={onRemove} className="ml-2 rounded p-1 text-[#7f8b90] hover:bg-[#263035] hover:text-[#dce2e2]" aria-label="Remove file">
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  )
}
