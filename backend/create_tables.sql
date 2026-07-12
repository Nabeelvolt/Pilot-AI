-- Submitted application documents (the actual PDFs submitted with an application)
create table if not exists application_documents (
  application_doc_id    text primary key,
  analysis_id           text,
  filename              text not null,
  document_category     text not null,
  -- Categories: flood_risk_assessment | heritage_impact_statement |
  -- design_access_statement | biodiversity_net_gain | energy_statement |
  -- transport_assessment | noise_assessment | planning_statement |
  -- structural_survey | drainage_strategy | other
  storage_path          text not null,
  extracted_text        text,
  word_count            integer,
  upload_status         text default 'uploaded',
  -- uploaded | extracted | analysed | error
  created_at            timestamptz default now()
);

-- Per-document policy compliance checks
create table if not exists document_assessments (
  assessment_id         text primary key,
  analysis_id           text not null,
  application_doc_id    text references application_documents(application_doc_id),
  document_category     text not null,
  overall_adequacy      text not null,
  -- ADEQUATE | INADEQUATE | MISSING_SECTIONS | CANNOT_ASSESS
  adequacy_score        float,
  sections_present      jsonb default '[]',
  sections_missing      jsonb default '[]',
  policy_conflicts      jsonb default '[]',
  recommendations       jsonb default '[]',
  created_at            timestamptz default now()
);

-- Validation checklist results
create table if not exists validation_results (
  validation_id         text primary key,
  analysis_id           text not null,
  application_type      text not null,
  required_documents    jsonb not null,
  -- Array of {document_name, required, present, adequate}
  overall_status        text not null,
  -- VALID | INVALID | REQUIRES_REVIEW
  missing_documents     jsonb default '[]',
  inadequate_documents  jsonb default '[]',
  created_at            timestamptz default now()
);
