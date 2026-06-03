'use client';
import { useState } from 'react';
import { AnalysisRequest } from '@/lib/types';

interface Props {
  onSubmit: (data: AnalysisRequest) => void;
  disabled: boolean;
}

export default function ApplicationForm({ onSubmit, disabled }: Props) {
  const [ref, setRef] = useState('');
  const [address, setAddress] = useState('');
  const [type, setType] = useState('Full Planning Permission');
  const [dev, setDev] = useState('');
  const [constraints, setConstraints] = useState<string[]>([]);

  const constraintOptions = [
    'Conservation Area', 'Green Belt', 'Flood Zone 2', 'Flood Zone 3',
    'Article 4 Direction', 'Grade I Listed Building', 'Grade II* Listed Building',
    'Grade II Listed Building', 'Tree Preservation Order', 'SSSI', 'None known'
  ];

  const handleDemoFill = () => {
    setRef('APP/2025/0187');
    setAddress('Former garage site, 14–18 Brayford Street, Lincoln, LN1 3XX');
    setType('Full Planning Permission');
    setDev('Demolition of existing garages and erection of a 3-storey residential block comprising 12 apartments (8 × 2-bed, 4 × 1-bed) with associated parking (6 spaces) and communal landscaping');
    setConstraints(['Conservation Area', 'Flood Zone 2']);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (dev.length < 50) return;
    
    onSubmit({
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
            <label className="block text-sm font-medium text-slate-700 mb-1">Site Address</label>
            <input 
              type="text" value={address} onChange={e => setAddress(e.target.value)} required
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

        <button
          type="submit"
          disabled={disabled || dev.length < 50}
          className="w-full bg-brand-navy hover:bg-brand-sky transition-colors text-white font-bold py-3 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center justify-center"
        >
          <span>{disabled ? 'Analysing...' : 'Analyse Application'}</span>
          <span className="text-xs font-normal text-slate-300 mt-0.5 opacity-80">Powered by Groq Llama 3.3 70B (free)</span>
        </button>
      </form>
    </div>
  );
}
