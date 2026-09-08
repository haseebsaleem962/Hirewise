'use client';
import { useCallback, useState } from 'react';
import { Upload, X, FileText, Loader2 } from 'lucide-react';

interface Props { onFilesSelected: (files: File[]) => void; isUploading?: boolean; }

export default function ResumeUpload({ onFilesSelected, isUploading }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [drag, setDrag] = useState(false);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDrag(false);
    setFiles((p) => [...p, ...Array.from(e.dataTransfer.files).filter((f) => f.name.endsWith('.pdf') || f.name.endsWith('.docx'))]);
  }, []);

  const onInput = (e: React.ChangeEvent<HTMLInputElement>) => { if (e.target.files) setFiles((p) => [...p, ...Array.from(e.target.files!)]); };
  const remove = (i: number) => setFiles((p) => p.filter((_, idx) => idx !== i));
  const submit = () => { if (files.length > 0) { onFilesSelected(files); setFiles([]); } };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        className={`relative border-2 border-dashed rounded-[var(--radius-card)] p-12 text-center transition-all duration-300 ${
          drag ? 'border-indigo-400 bg-indigo-50/50 dark:bg-indigo-950/20 scale-[1.005]' : 'border-[var(--color-border)] bg-[var(--color-surface-alt)] hover:border-indigo-300'
        }`}
      >
        <div className="mx-auto w-14 h-14 rounded-2xl bg-[var(--color-primary-soft)] flex items-center justify-center mb-4">
          <Upload size={22} className="text-[var(--color-primary)]" />
        </div>
        <p className="text-[14px] font-semibold text-[var(--color-text)]">Drop resumes here or browse files</p>
        <p className="text-[12px] text-[var(--color-text-muted)] mt-1">PDF & DOCX — up to 80 files at once</p>
        <label className="btn-primary mt-5 cursor-pointer inline-flex">
          <Upload size={14} /> Browse Files
          <input type="file" multiple accept=".pdf,.docx" onChange={onInput} className="hidden" />
        </label>
      </div>

      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-[12px] font-semibold text-[var(--color-text-secondary)]">{files.length} file(s) ready</p>
            <button onClick={() => setFiles([])} className="text-[11px] font-semibold text-[var(--color-danger)] hover:underline">Clear all</button>
          </div>
          <div className="max-h-44 overflow-y-auto space-y-1.5">
            {files.map((f, i) => (
              <div key={i} className="flex items-center justify-between px-3.5 py-2 rounded-[var(--radius-input)] bg-[var(--color-surface)] border border-[var(--color-border)]">
                <div className="flex items-center gap-2.5 min-w-0">
                  <FileText size={13} className="text-[var(--color-primary)] shrink-0" />
                  <span className="text-[12px] text-[var(--color-text)] truncate">{f.name}</span>
                  <span className="text-[10px] text-[var(--color-text-muted)] shrink-0">{(f.size / 1024).toFixed(0)}KB</span>
                </div>
                <button onClick={() => remove(i)} className="text-[var(--color-danger)] hover:opacity-60 shrink-0 ml-2"><X size={13} /></button>
              </div>
            ))}
          </div>
          <button onClick={submit} disabled={isUploading} className="btn-primary w-full justify-center py-3 text-[13px] disabled:opacity-40 disabled:pointer-events-none">
            {isUploading ? <><Loader2 size={15} className="animate-spin" /> Processing {files.length} resume(s)...</> : `Upload & Screen ${files.length} Resume(s)`}
          </button>
        </div>
      )}
    </div>
  );
}
