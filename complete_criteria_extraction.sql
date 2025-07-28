-- ================================================================
-- COMPLETE DELOITTE CRITERIA WITH EXTRACTED VERBATIM CONTENT
-- All 12 active criteria with tags extracted to existing columns
-- ================================================================

USE ROLE top_200_role;
USE WAREHOUSE top_200_wh;
USE DATABASE top_200_db;
USE SCHEMA top_200_schema;

-- Clear existing criteria data
DELETE FROM input_criteria WHERE version = '20250723';

-- A.1: Strategy & Planning Cycle - Long-term outlook
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'A.1',
    'Does the business show a long-term outlook, minimum longer then 5 years, counting from the year of publication, specifically for its sustainability strategy, and planning cycle? If not this should answer a ''no'' including the planning/outlook/performance period extending to year.',
    ARRAY_CONSTRUCT('Strategy', 'Planning cycle'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>A.1 <cluster>Strategy, Planning cycle</cluster><question>Does the business show a long-term outlook, minimum longer then 5 years, counting from the year of publication, specifically for its sustainability strategy, and planning cycle? If not this should answer a ''no'' including the planning/outlook/performance period extending to year.</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question A.1</task>',
    0.05,
    '20250723',
    TRUE
);

-- A.2: Strategy & Planning Cycle - Sustainability integration
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'A.2',
    'Is sustainability integrated into the business model and/or central to its core strategy, showing that its is not treated as a separate issue. Indicate which parts of the business are involved (beyond governance and leadership)? Show evidence of the values, culture and or principles linked to sustainability (beyond climate change, for example biodiversity, human rights, circular economy)?',
    ARRAY_CONSTRUCT('Strategy', 'Planning cycle'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>A.2 <cluster>Strategy, Planning cycle</cluster><question>Is sustainability integrated into the business model and/or central to its core strategy, showing that its is not treated as a separate issue. Indicate which parts of the business are involved (beyond governance and leadership)? Show evidence of the values, culture and or principles linked to sustainability (beyond climate change, for example biodiversity, human rights, circular economy)?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question A.2</task>',
    0.05,
    '20250723',
    TRUE
);

-- A.4: Strategy & Planning Cycle - Regular review
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'A.4',
    'Is there evidence of a regular or on ongoing bases review (optional: and development) of the company''s sustainability strategy, that goes beyond only the emission reduction/decarbonisation strategy? In the answer mention how often a year is meant with regular/ongoing',
    ARRAY_CONSTRUCT('Strategy', 'Planning cycle'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>A.4 <cluster>Strategy, Planning cycle</cluster><question>Is there evidence of a regular or on ongoing bases review (optional: and development) of the company''s sustainability strategy, that goes beyond only the emission reduction/decarbonisation strategy? In the answer mention how often a year is meant with regular/ongoing</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question A.4</task>',
    0.05,
    '20250723',
    TRUE
);

-- B.1: Principles & Values - Company role in sustainable development
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'B.1',
    'Does the company articulate its role as a company as part of the economy/society/world in achieving sustainable development, so what does the company reconises both its impact of its operations have on the environment and society ("inside-out" or impact materiality), and how environmental and social issues affect the company''s own financial performance and value ("outside-in" or financial materiality). If so, provide evidence how they frame this for inside-out and/or outside-in perspective, and how it does the company manages these within it''s core business activities and responsibilities (not whitin governance/board level) beyond emission reduction/decarbonisation targets?',
    ARRAY_CONSTRUCT('Principles & values'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>B.1 <cluster>Principles & values</cluster><question>Does the company articulate its role as a company as part of the economy/society/world in achieving sustainable development, so what does the company reconises both its impact of its operations have on the environment and society ("inside-out" or impact materiality), and how environmental and social issues affect the company''s own financial performance and value ("outside-in" or financial materiality). If so, provide evidence how they frame this for inside-out and/or outside-in perspective, and how it does the company manages these within it''s core business activities and responsibilities (not whitin governance/board level) beyond emission reduction/decarbonisation targets?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question B.1</task>',
    0.05,
    '20250723',
    TRUE
);

-- B.2: Governance - CEO/MD Leadership
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'B.2',
    'Is there evidence that the CEO and MD both articulates and demonstrates strong leadership on material ESG matters? Show the evidence in one sentence or paragraphs it mention the Executive management and C-suite level that have the leadership specifically in relation to the ESG matters, not for general day-to-day management and responsibilities',
    ARRAY_CONSTRUCT('Governance'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>B.2 <cluster>Governance</cluster><question>Is there evidence that the CEO and MD both articulates and demonstrates strong leadership on material ESG matters? Show the evidence in one sentence or paragraphs it mention the Executive management and C-suite level that have the leadership specifically in relation to the ESG matters, not for general day-to-day management and responsibilities</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question B.2</task>',
    0.05,
    '20250723',
    TRUE
);

-- B.3: Governance - Executive Management Accountability
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'B.3',
    'Does the Executive Management have accountabilities/responsibilities (not remuneration-tied) for ensuring management of ESG issues, climate risk management and/or commitments to diversity and inclusion? If yes, say per boardmember which responsibilities',
    ARRAY_CONSTRUCT('Governance'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>B.3 <cluster>Governance</cluster><question>Does the Executive Management have accountabilities/responsibilities (not remuneration-tied) for ensuring management of ESG issues, climate risk management and/or commitments to diversity and inclusion? If yes, say per boardmember which responsibilities</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question B.3</task>',
    0.05,
    '20250723',
    TRUE
);

-- B.4: Governance - ESG Performance-tied Compensation
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'B.4',
    'Does the company has for this year report, ESG performance-tied bonuses/remuneration/compensation for Executive / C-suite level? If yes, only mention for what ESG-related performance/KPIs and for which Executive / C-suite level',
    ARRAY_CONSTRUCT('Governance'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>B.4 <cluster>Governance</cluster><question>Does the company has for this year report, ESG performance-tied bonuses/remuneration/compensation for Executive / C-suite level? If yes, only mention for what ESG-related performance/KPIs and for which Executive / C-suite level</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question B.4</task>',
    0.05,
    '20250723',
    TRUE
);

-- C.1: Risk Management - ESG Systems & Policies
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'C.1',
    'Does the company detail current systems, policies, practices and/or procedures (not related to executive management/leadership responsibilities/accountabilities/overseeing and reporting standards and assurance) to manage material ESG issues, beyond decarbonisation/greenhouse gas emissions including for example climate change, biodiversity, human rights?',
    ARRAY_CONSTRUCT('Risk Management'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>C.1 <cluster>Risk Management</cluster><question>Does the company detail current systems, policies, practices and/or procedures (not related to executive management/leadership responsibilities/accountabilities/overseeing and reporting standards and assurance) to manage material ESG issues, beyond decarbonisation/greenhouse gas emissions including for example climate change, biodiversity, human rights?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question C.1</task>',
    0.083333333,
    '20250723',
    TRUE
);

-- C.2: Strategy & Risk Management - ESG Strategy Addressing Risks
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'C.2',
    'Does the ESG strategy (incl targets) addressed material ESG risks, beyond only identifying and assessing it internally?  . i.e. negative externalities arising from core business activities (such as emissions linked to high fossil fuel dependency; indentured labour in the supply chain etc) If yes, indicate what the mitigation activities are implemented.',
    ARRAY_CONSTRUCT('Strategy', 'Risk management'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>C.2 <cluster>Strategy, Risk management</cluster><question>Does the ESG strategy (incl targets) addressed material ESG risks, beyond only identifying and assessing it internally?  . i.e. negative externalities arising from core business activities (such as emissions linked to high fossil fuel dependency; indentured labour in the supply chain etc) If yes, indicate what the mitigation activities are implemented.</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question C.2</task>',
    0.083333333,
    '20250723',
    TRUE
);

-- C.3: Strategy, Supply Chain & Operations - Business Evolution
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'C.3',
    'Does the business strategy articulate how the business is evolving to become more sustainability oriented with their actual core business activities (beyond internal operations such as reporting, governance, risk management, remuneration etc.), e.g. their production or service offerings? Show this with detailing the clear KPIs, with time-bound targets and pathways to meet its targets, beyond carbon emissions/decarbonisation?',
    ARRAY_CONSTRUCT('Strategy', 'Supply chain management', 'Operations'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>C.3 <cluster>Strategy, Supply chain management, Operations</cluster><question>Does the business strategy articulate how the business is evolving to become more sustainability oriented with their actual core business activities (beyond internal operations such as reporting, governance, risk management, remuneration etc.), e.g. their production or service offerings? Show this with detailing the clear KPIs, with time-bound targets and pathways to meet its targets, beyond carbon emissions/decarbonisation?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question C.3</task>',
    0.083333333,
    '20250723',
    TRUE
);

-- C.4: Strategy & Engagement Management - Stakeholder Outcomes
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'C.4',
    'Is there evidence of the company having positive/beneficial outcomes for stakeholders, including employees and the communities in which it operates, and/or Iwi''s it impacts, by improving the impact on these stakeholders wellbeing and/or working together with these stakeholders?',
    ARRAY_CONSTRUCT('Strategy', 'Engagement management'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>C.4 <cluster>Strategy, Engagement management</cluster><question>Is there evidence of the company having positive/beneficial outcomes for stakeholders, including employees and the communities in which it operates, and/or Iwi''s it impacts, by improving the impact on these stakeholders wellbeing and/or working together with these stakeholders?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question C.4</task>',
    0.083333333,
    '20250723',
    TRUE
);

-- C.5: Engagement Management & Governance - Active Stakeholder Engagement
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'C.5',
    'Is there evidence of the company actively engaging with its stakeholders, such as employees, local communities, iwi''s etc. and can it demonstrate that its strategy actively addresses these stakeholder concerns and wellbeing?',
    ARRAY_CONSTRUCT('Engagement management', 'Governance'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>C.5 <cluster>Engagement management, Governance</cluster><question>Is there evidence of the company actively engaging with its stakeholders, such as employees, local communities, iwi''s etc. and can it demonstrate that its strategy actively addresses these stakeholder concerns and wellbeing?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question C.5</task>',
    0.083333333,
    '20250723',
    TRUE
);

-- C.6: Metrics & Targets, Reporting - Carbon Performance
INSERT INTO input_criteria (
    id, question, cluster, role, instructions, output, 
    criteria_prompt, weight, version, active
) VALUES (
    'C.6',
    'Is there evidence of performance against CARBON targets on tonnes Co2/GHG emissions on scope 1, 2 and 3 (and potentially intesity) with demonstrating a track record over the past (at least 5) financial years and progress towards carbon targets? If so, indicate if it shows a positive performance against the targets''s progress towards stated carbon targets?',
    ARRAY_CONSTRUCT('Metrics & Targets', 'Reporting'),
    'You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.',
    '1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.',
    'in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }',
    '<role> You are an expert ESG analyst working at Deloitte for last 20 years, you have gathered extensive expertise in the domain.</role><instructions>1. your job is to assess a company based on the information shared in their annual report.2. Only answer based on the information provided in the report.3. Output based on the specified format, Do not output anything else.4. You are given a series of questions that pertain to a specfic topic in the analysis/ research. Your job is to focus on one question at a time. And make sure that the answers do not overlap. Each question belong to one or more cluster, mentioned in <cluster> tags.5. quote the verbatim from the <context> tags as supporting_evidence. Do not summarize these quotes while providing the supporting_evidence. Provide them as they appear in the <context> tags.</instructions><questions>C.6 <cluster>Metrics & Targets, Reporting</cluster><question>Is there evidence of performance against CARBON targets on tonnes Co2/GHG emissions on scope 1, 2 and 3 (and potentially intesity) with demonstrating a track record over the past (at least 5) financial years and progress towards carbon targets? If so, indicate if it shows a positive performance against the targets''s progress towards stated carbon targets?</question></questions><o>in a json format {result: ''yes'' or ''no'', ''supporting_evidence'': [{1: ''verbatim quote from the retrieved document chunk''}, {2:''another verbatim quote from the retrieved document chunk''}], ''explanation'' : ''text'' }</o><task>Answer question C.6</task>',
    0.083333333,
    '20250723',
    TRUE
);

-- Display success message
SELECT 'All 12 Deloitte criteria imported with extracted verbatim content!' as status,
       COUNT(*) as criteria_count
FROM input_criteria 
WHERE version = '20250723';

-- Show summary by cluster
SELECT 
    ARRAY_TO_STRING(cluster, ', ') as cluster_group,
    COUNT(*) as criteria_count,
    ROUND(AVG(weight), 3) as avg_weight
FROM input_criteria 
WHERE version = '20250723' AND active = TRUE
GROUP BY cluster
ORDER BY criteria_count DESC; 