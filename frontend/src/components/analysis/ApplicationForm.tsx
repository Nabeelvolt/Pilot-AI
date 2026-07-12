'use client';
import { useState, useEffect } from 'react';
import { AnalysisRequest } from '@/lib/types';
import { API_BASE } from '@/lib/api';

interface Props {
  onSubmit: (data: AnalysisRequest) => void;
  disabled: boolean;
}

export default function ApplicationForm({ onSubmit, disabled }: Props) {
  const [analysisId] = useState(() => typeof crypto !== 'undefined' ? crypto.randomUUID() : 'temp-id-' + Date.now());
  const [ref, setRef] = useState('');
  const [address, setAddress] = useState('');
  const [type, setType] = useState('Full Planning Permission');
  const [dev, setDev] = useState('');
  const [constraints, setConstraints] = useState<string[]>([]);
  
  const [isDetecting, setIsDetecting] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState<{name: string, status: string}[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const constraintOptions = [
    'Conservation Area', 'Green Belt', 'Flood Zone 2', 'Flood Zone 3',
    'Article 4 Direction', 'Grade I Listed Building', 'Grade II* Listed Building',
    'Grade II Listed Building', 'Tree Preservation Order', 'SSSI', 'None known'
  ];

  const handleDemoFill = () => {
    setRef('APP/2025/0187');
    setAddress('14-18 Brayford Street, Lincoln LN1 3XX');
    setType('Full Planning Permission');
    setDev('Demolition of existing garages and erection of a 3-storey residential block comprising 12 apartments (8 × 2-bed, 4 × 1-bed) with associated parking (6 spaces) and communal landscaping');
    setConstraints(['Conservation Area', 'Flood Zone 2']);
  };

  const handleAutoDetect = async () => {
    if (!address || address.length < 5) {
      alert('Please enter a valid address with postcode to auto-detect constraints.');
      return;
    }
    setIsDetecting(true);
    try {
      const res = await fetch(`${API_BASE}/applications/detect-constraints?address=${encodeURIComponent(address)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.suggested_checkboxes) {
          const newConstraints = data.suggested_checkboxes.filter((c: string) => constraintOptions.includes(c));
          if (newConstraints.length > 0) {
            setConstraints(newConstraints);
          } else {
            setConstraints(['None known']);
          }
        }
      } else {
        console.error('Detection failed');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsDetecting(false);
    }
  };

  const processFiles = async (files: FileList | File[] | null) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadError('');

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setUploadedDocs(prev => [...prev, { name: file.name, status: 'Uploading...' }]);
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('analysis_id', analysisId);
        
        // Let's guess doc category based on filename (simple heuristic)
        let docCategory = 'Other';
        const nameLower = file.name.toLowerCase();
        if (nameLower.includes('form') || nameLower.includes('application')) docCategory = 'Application Form';
        else if (nameLower.includes('plan') || nameLower.includes('drawing')) docCategory = 'Plans & Drawings';
        else if (nameLower.includes('design') || nameLower.includes('das')) docCategory = 'Design & Access Statement';
        else if (nameLower.includes('heritage')) docCategory = 'Heritage Statement';
        else if (nameLower.includes('flood') || nameLower.includes('fra')) docCategory = 'Flood Risk Assessment';
        else if (nameLower.includes('energy')) docCategory = 'Energy Statement';
        else if (nameLower.includes('biodiversity') || nameLower.includes('bng')) docCategory = 'Biodiversity Net Gain Assessment';
        
        formData.append('doc_category', docCategory);

        const res = await fetch(`${API_BASE}/document-analysis/upload`, {
          method: 'POST',
          body: formData,
        });

        if (res.ok) {
          setUploadedDocs(prev => prev.map(d => d.name === file.name ? { ...d, status: 'Success' } : d));
        } else {
          setUploadedDocs(prev => prev.map(d => d.name === file.name ? { ...d, status: 'Failed' } : d));
        }
      }
    } catch (err) {
      console.error(err);
      setUploadError('Failed to upload some documents.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files);
    if (e.target) e.target.value = ''; // Reset input
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    processFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (dev.length < 50) return;
    
    onSubmit({
      analysis_id: analysisId,
      application_ref: ref,
      site_address: address,
      application_type: type,
      proposed_development: dev,
      site_constraints: constraints.includes('None known') ? [] : constraints,
    });
  };

  const toggleConstraint = (c: string) => {
    if (c === 'None known') {
      setConstraints(['None known']);
      return;
    }
    let newC = constraints.filter(x => x !== 'None known');
    if (newC.includes(c)) {
      newC = newC.filter(x => x !== c);
    } else {
      newC.push(c);
    }
    setConstraints(newC);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
        <h2 className="text-lg font-bold text-slate-800">Application Details</h2>
        <button 
          type="button" 
          onClick={handleDemoFill}
          className="text-sm bg-brand-ice text-brand-sky hover:bg-brand-sky hover:text-white px-3 py-1.5 rounded transition-colors font-medium"
        >
          Use Demo Application
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Application Reference (Optional)</label>
            <input 
              type="text" value={ref} onChange={e => setRef(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-brand-sky focus:border-brand-sky text-sm"
            />
          </div>
          <div>
            <div className="flex justify-between items-end mb-1">
              <label className="block text-sm font-medium text-slate-700">Site Address</label>
              <button type="button" onClick={handleAutoDetect} disabled={isDetecting || !address} className="text-xs text-brand-sky font-medium hover:underline disabled:opacity-50">
                {isDetecting ? 'Detecting...' : 'Auto-detect constraints'}
              </button>
            </div>
            <input 
              type="text" value={address} onChange={e => setAddress(e.target.value)} required
              placeholder="Enter full address including postcode..."
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-brand-sky focus:border-brand-sky text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Application Type</label>
          <select 
            value={type} onChange={e => setType(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-brand-sky focus:border-brand-sky text-sm"
          >
            <option>Full Planning Permission</option>
            <option>Listed Building Consent</option>
            <option>Change of Use</option>
            <option>Householder Application</option>
            <option>Prior Approval</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Proposed Development</label>
          <textarea 
            value={dev} onChange={e => setDev(e.target.value)} required rows={4}
            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-brand-sky focus:border-brand-sky text-sm"
          />
          <div className="flex justify-end mt-1">
            <span className={`text-xs ${dev.length < 50 ? 'text-red-500 font-medium' : 'text-slate-500'}`}>
              {dev.length} / 50 min characters
            </span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">Site Constraints</label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-50 p-4 rounded-md border border-slate-100">
            {constraintOptions.map(c => (
              <label key={c} className="flex items-center space-x-2 text-sm text-slate-700 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={constraints.includes(c)}
                  onChange={() => toggleConstraint(c)}
                  className="rounded text-brand-sky focus:ring-brand-sky"
                />
                <span>{c}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Document Upload Section */}
        <div className="bg-slate-50 p-4 rounded-md border border-slate-200">
          <label className="block text-sm font-bold text-slate-800 mb-2">Upload Document Bundle (PDFs)</label>
          <p className="text-xs text-slate-500 mb-4">Upload PDFs for validation checking and policy assessment. They will be linked to this analysis.</p>
          <div className="flex items-center justify-center w-full">
              <label 
                className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-white hover:bg-slate-50"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <svg className="w-8 h-8 mb-3 text-slate-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                          <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                      </svg>
                      <p className="mb-2 text-sm text-slate-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                      <p className="text-xs text-slate-500">PDF documents only</p>
                  </div>
                  <input type="file" className="hidden" multiple accept="application/pdf" onChange={handleFileUpload} disabled={isUploading} />
              </label>
          </div>
          {uploadedDocs.length > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-slate-700 mb-2">Uploaded Files</h4>
              <ul className="text-xs space-y-1">
                {uploadedDocs.map((doc, idx) => (
                  <li key={idx} className="flex justify-between items-center text-slate-600 bg-white p-2 rounded border border-slate-100">
                    <span className="truncate max-w-[80%]">{doc.name}</span>
                    <span className={`font-medium ${doc.status === 'Success' ? 'text-green-600' : doc.status === 'Failed' ? 'text-red-600' : 'text-amber-500'}`}>{doc.status}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {uploadError && <p className="text-xs text-red-500 mt-2">{uploadError}</p>}
        </div>

        <button
          type="submit"
          disabled={disabled || dev.length < 50 || isUploading}
          className="w-full bg-brand-navy hover:bg-brand-sky transition-colors text-white font-bold py-3 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center justify-center"
        >
          <span>{disabled ? 'Analysing...' : 'Analyse Application'}</span>
          <span className="text-xs font-normal text-slate-300 mt-0.5 opacity-80">Powered by Groq Llama 3.3 70B (free)</span>
        </button>
      </form>
    </div>
  );
}
