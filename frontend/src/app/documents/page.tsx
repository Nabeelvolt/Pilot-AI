'use client';
import { useEffect, useState } from 'react';
import TopBar from '@/components/layout/TopBar';
import StatusPill from '@/components/ui/StatusPill';
import Badge from '@/components/ui/Badge';
import { getDocuments, uploadDocument, checkHealth } from '@/lib/api';
import { DocumentRecord } from '@/lib/types';

export default function Documents() {
  const [docs, setDocs] = useState<DocumentRecord[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Form state
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [type, setType] = useState('national_policy');
  const [lpa, setLpa] = useState('national');

  const refresh = () => {
    getDocuments().then(setDocs).catch(console.error);
    checkHealth().then(setHealth).catch(console.error);
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_title', title);
    formData.append('doc_type', type);
    formData.append('lpa_code', lpa);

    try {
      await uploadDocument(formData);
      setFile(null);
      setTitle('');
      refresh();
    } catch (err) {
      alert('Upload failed: ' + err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-50">
      <TopBar title="Policy Library" />
      
      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        
        {/* Summary Bar */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-100 flex items-center justify-between">
          <div className="flex gap-8">
            <div>
              <span className="text-sm text-slate-500 mr-2">Total Documents:</span>
              <span className="font-bold text-slate-800">{docs.length}</span>
            </div>
            <div>
              <span className="text-sm text-slate-500 mr-2">Total Chunks Searchable:</span>
              <span className="font-bold text-slate-800">{health?.total_chunks_indexed || 0}</span>
            </div>
          </div>
          <div>
            <span className="text-sm text-slate-500 mr-2">Embedding Model:</span>
            <Badge variant="info">{health?.embedding_model || 'Loading...'}</Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Card Grid */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-bold text-slate-800">Indexed Documents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {docs.map(doc => (
                <div key={doc.doc_id} className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-slate-900 leading-tight">{doc.document_title}</h3>
                    <StatusPill status={doc.status.toUpperCase()} />
                  </div>
                  <div className="text-sm text-slate-500 mb-4">{doc.filename}</div>
                  
                  <div className="flex items-center gap-2 mb-4">
                    <Badge>{doc.doc_type}</Badge>
                    <Badge>{doc.lpa_code}</Badge>
                  </div>
                  
                  <div className="flex justify-between text-xs text-slate-400 border-t border-slate-100 pt-3">
                    <span>{doc.chunk_count} chunks indexed</span>
                    <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
              {docs.length === 0 && (
                <div className="col-span-2 p-8 text-center text-slate-500 bg-white rounded-xl border border-dashed border-slate-300">
                  No documents indexed yet.
                </div>
              )}
            </div>
          </div>

          {/* Upload Section */}
          <div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 sticky top-0">
              <h2 className="text-lg font-bold text-slate-800 mb-4">Upload New Policy</h2>
              
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">PDF File</label>
                  <input 
                    type="file" 
                    accept=".pdf"
                    required
                    onChange={e => setFile(e.target.files?.[0] || null)}
                    className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-brand-ice file:text-brand-sky hover:file:bg-brand-ice/80"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Document Title</label>
                  <input 
                    type="text" 
                    required
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-brand-sky focus:border-brand-sky text-sm"
                    placeholder="e.g. Lincoln Design Guide"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Document Type</label>
                  <select 
                    value={type}
                    onChange={e => setType(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-brand-sky focus:border-brand-sky text-sm"
                  >
                    <option value="national_policy">National Policy</option>
                    <option value="local_plan">Local Plan</option>
                    <option value="spd">SPD / Guidance</option>
                    <option value="building_regs">Building Regulations</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">LPA / Scope</label>
                  <select 
                    value={lpa}
                    onChange={e => setLpa(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-brand-sky focus:border-brand-sky text-sm"
                  >
                    <option value="national">National</option>
                    <option value="lincoln">Lincoln</option>
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={isUploading || !file || !title}
                  className="w-full bg-brand-navy hover:bg-brand-sky transition-colors text-white font-medium py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Uploading & Indexing...' : 'Upload & Index PDF'}
                </button>
              </form>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
