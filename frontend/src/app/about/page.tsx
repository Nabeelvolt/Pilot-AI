'use client';
import TopBar from '@/components/layout/TopBar';

export default function About() {
  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-50">
      <TopBar title="Welcome to the PILOT-AI Focus Group" />
      
      <div className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full space-y-8">
        
        {/* v0.2 update notice */}
        <div className="bg-brand-teal text-white rounded-xl p-6 mb-8 shadow-sm">
          <h2 className="text-xl font-bold mb-3">
            🆕 What&apos;s New in v0.2 — Following Your Feedback
          </h2>
          <p className="text-sm text-teal-100 mb-4">
            Following our focus group session on 25 June 2026 with senior planning
            officers from Central Lincolnshire Local Planning Authorities, PILOT-AI
            v0.2 introduces:
          </p>
          <ul className="space-y-2">
            {[
              'Document bundle upload — upload the actual PDFs submitted with an application',
              'Content adequacy checking — AI reviews whether each document meets policy requirements, not just whether it is present',
              'Automatic constraint detection — enter a postcode and the system detects flood zones, listed buildings, Article 4 Directions, and conservation areas using Environment Agency and MHCLG open data',
              'Validation checklist — checks compliance with GOV.UK national requirements and the Central Lincolnshire Local Validation Lists (adopted May 2024)',
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="mt-0.5 shrink-0 text-teal-200">✓</span>
                <span className="text-teal-50">{item}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-teal-200 border-t border-teal-500 pt-3">
            Implemented specifically based on feedback from Julie Mason (Principal
            Planning Officer) who described flood risk assessments that pass
            validation by name but fail on content — and from Chris Harrison who
            requested discharge of conditions document screening.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
          <h2 className="text-xl font-bold text-slate-800 mb-4">What PILOT-AI does</h2>
          <ul className="list-disc pl-5 space-y-2 text-slate-700 mb-8">
            <li>Reads a planning application description and finds every relevant national and local planning policy</li>
            <li>Produces a structured compliance report with every finding linked to the exact policy clause</li>
            <li>Helps planning officers work faster and more consistently — without replacing their judgement</li>
          </ul>

          <h2 className="text-xl font-bold text-slate-800 mb-4">What PILOT-AI does NOT do</h2>
          <ul className="list-disc pl-5 space-y-2 text-slate-700 mb-8">
            <li>Make planning decisions or recommend approval/refusal</li>
            <li>Replace the planning officer's professional expertise and legal responsibility</li>
            <li>Access live GIS data or check current site conditions</li>
          </ul>

          <h2 className="text-xl font-bold text-slate-800 mb-4">How to read the report</h2>
          <p className="text-slate-700 mb-4">
            The compliance status indicates whether the application appears to align with policy based strictly on the text provided.
            The <strong>Confidence Score</strong> indicates how much relevant policy context the AI was able to retrieve to make its assessment — it is NOT a prediction of the final planning outcome.
            Always review the specific citations to verify the AI's reasoning.
          </p>

          <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-8">
            <h3 className="font-bold text-amber-800 mb-1">AI limitations notice</h3>
            <p className="text-amber-700 text-sm">
              PILOT-AI can only assess what it finds in its loaded policy library. This demo contains 3 sample documents covering Lincoln. A production system would contain hundreds of documents. Always verify against your authority's current adopted policies.
            </p>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <h3 className="font-bold text-emerald-800 mb-1">This demo is free</h3>
            <p className="text-emerald-700 text-sm">
              This prototype uses Groq's free API (Llama 3.3 70B) and locally-running sentence embeddings. It costs £0.00 to run. There are no cloud subscriptions or API fees.
            </p>
          </div>
        </div>

        <div className="bg-brand-navy text-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-brand-ice mb-6">Focus Group Discussion Questions</h2>
          <ol className="list-decimal pl-5 space-y-4 text-lg">
            <li>Does this output give you useful information you didn't already have?</li>
            <li>Do you trust the cited policy text? Would you click through to verify it independently?</li>
            <li>Is the language clear enough to support a delegated report or officer note?</li>
            <li>What is missing that you would need before using this in practice?</li>
            <li>How would this change your current workflow — what would you do differently?</li>
            <li>What would make you uncomfortable about using an AI system like this?</li>
          </ol>
        </div>

      </div>
    </div>
  );
}
