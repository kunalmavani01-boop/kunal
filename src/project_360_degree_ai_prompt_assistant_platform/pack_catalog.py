"""Curated prompt pack catalog for the local beta experience."""

from __future__ import annotations


PACK_CATALOG = [
    {
        "category": "Writing & Content",
        "pack": "Blog Outline Pack",
        "domain": "Marketing",
        "interest": "Content Writers",
        "use_case": "Turn a rough topic into a publishable content structure.",
        "keywords": ["blog", "article", "seo", "outline", "content", "post", "newsletter"],
        "common_missing_elements": ["audience", "goal", "format", "tone"],
        "repair_hints": [
            "Name the audience so the outline targets the right depth.",
            "State whether the goal is traffic, education, or conversion.",
            "Add a format target such as H1, H2s, bullets, or CTA section.",
        ],
        "templates": [
            {
                "id": "blog-outline-seo",
                "title": "SEO Blog Outline Builder",
                "subcategory": "SEO Outlines",
                "summary": "Build a search-friendly outline with headers, intent, and CTA.",
                "template_fields": ["topic", "audience", "search_intent", "tone", "cta"],
                "keywords": ["seo", "blog", "outline", "headers", "search"],
                "why_it_works": [
                    "Adds audience and search intent.",
                    "Creates a usable section structure.",
                    "Ends with a clear CTA so the post has a purpose.",
                ],
                "prompt_text": (
                    "Write an SEO blog outline about [topic] for [audience]. "
                    "The reader intent is [search_intent]. Use a [tone] tone. "
                    "Return an H1, 5-7 H2 sections, a short intro angle, and a final CTA focused on [cta]."
                ),
            },
            {
                "id": "blog-outline-thought-leadership",
                "title": "Thought Leadership Post Planner",
                "subcategory": "Thought Leadership",
                "summary": "Shape a founder-style or expert-style post into a clear argument.",
                "template_fields": ["topic", "audience", "core_opinion", "proof_points", "tone"],
                "keywords": ["thought leadership", "opinion", "founder", "expert", "insight"],
                "why_it_works": [
                    "Forces a point of view instead of generic filler.",
                    "Adds proof points so the writing sounds credible.",
                    "Improves structure for long-form content.",
                ],
                "prompt_text": (
                    "Create a thought leadership outline on [topic] for [audience]. "
                    "The core opinion is [core_opinion]. Use these proof points: [proof_points]. "
                    "Keep the voice [tone]. Return a hook, argument flow, counterpoint, and conclusion."
                ),
            },
            {
                "id": "blog-outline-newsletter",
                "title": "Newsletter Content Builder",
                "subcategory": "Newsletter Drafts",
                "summary": "Turn a rough update into a scannable newsletter structure.",
                "template_fields": ["topic", "audience", "main_takeaway", "tone", "cta"],
                "keywords": ["newsletter", "email content", "digest", "update"],
                "why_it_works": [
                    "Makes the takeaway explicit.",
                    "Keeps the structure scannable.",
                    "Adds an action step so the piece is useful.",
                ],
                "prompt_text": (
                    "Draft a newsletter structure about [topic] for [audience]. "
                    "The main takeaway is [main_takeaway]. Use a [tone] tone. "
                    "Return a subject line, opening, 3 main sections, and a CTA around [cta]."
                ),
            },
        ],
    },
    {
        "category": "Writing & Content",
        "pack": "Email Writing Pack",
        "domain": "Marketing",
        "interest": "Outreach",
        "use_case": "Write short, purposeful emails that drive a specific response.",
        "keywords": ["email", "outreach", "reply", "subject line", "cold email", "follow-up"],
        "common_missing_elements": ["recipient", "goal", "desired action", "word limit"],
        "repair_hints": [
            "Name who the email is for so the tone fits the reader.",
            "Say what response you want after the email is read.",
            "Add a word limit so the email stays concise.",
        ],
        "templates": [
            {
                "id": "email-cold-outreach",
                "title": "Cold Outreach Email Builder",
                "subcategory": "Cold Outreach",
                "summary": "Write a compact cold email with a low-friction CTA.",
                "template_fields": ["product", "recipient_role", "pain_point", "proof", "cta"],
                "keywords": ["cold email", "outreach", "sales", "reply"],
                "why_it_works": [
                    "Adds a clear pain point and proof.",
                    "Keeps the ask simple.",
                    "Reduces fluff that wastes tokens.",
                ],
                "prompt_text": (
                    "Draft a cold outreach email for [product] to a [recipient_role]. "
                    "Their likely pain point is [pain_point]. Include this proof or credibility signal: [proof]. "
                    "Keep it under 120 words and end with a CTA asking them to [cta]."
                ),
            },
            {
                "id": "email-follow-up",
                "title": "Follow-up Email Builder",
                "subcategory": "Follow-ups",
                "summary": "Write a professional follow-up without sounding pushy.",
                "template_fields": ["previous_context", "recipient_role", "desired_action", "tone"],
                "keywords": ["follow-up", "checking in", "reminder", "professional"],
                "why_it_works": [
                    "Adds context from the earlier interaction.",
                    "Makes the next step obvious.",
                    "Prevents awkward or repetitive wording.",
                ],
                "prompt_text": (
                    "Write a follow-up email to a [recipient_role]. "
                    "Previous context: [previous_context]. "
                    "Use a [tone] tone and end with a simple ask to [desired_action]. Keep it concise."
                ),
            },
            {
                "id": "email-launch-announcement",
                "title": "Launch Email Planner",
                "subcategory": "Launch Emails",
                "summary": "Turn a product launch idea into a clean launch email structure.",
                "template_fields": ["product", "audience", "main_benefit", "tone", "cta"],
                "keywords": ["launch", "announcement", "product update", "release"],
                "why_it_works": [
                    "Clarifies audience and benefit early.",
                    "Adds a clear structure for announcement emails.",
                    "Makes the CTA explicit.",
                ],
                "prompt_text": (
                    "Write a launch email for [product] to [audience]. "
                    "The main benefit is [main_benefit]. Use a [tone] tone. "
                    "Return a subject line, opening, 3 short benefit bullets, and a CTA to [cta]."
                ),
            },
        ],
    },
    {
        "category": "Business & Strategy",
        "pack": "Product Strategy Pack",
        "domain": "Business",
        "interest": "Founders",
        "use_case": "Shape a product, platform, or startup idea into a clearer strategic prompt.",
        "keywords": [
            "product",
            "platform",
            "app",
            "website",
            "startup",
            "business idea",
            "market gap",
            "feature",
            "roadmap",
            "strategy",
            "mvp",
        ],
        "common_missing_elements": ["user problem", "target audience", "differentiator", "success criteria"],
        "repair_hints": [
            "Name the user problem before asking for features or positioning.",
            "Add the target audience so the strategy stays anchored to real users.",
            "State the differentiator or market gap you want the answer to sharpen.",
        ],
        "templates": [
            {
                "id": "product-strategy-brief",
                "title": "Product Strategy Brief",
                "subcategory": "Product Strategy",
                "summary": "Turn a rough product idea into a clearer strategy prompt with audience, gap, and positioning.",
                "template_fields": ["product", "audience", "pain_point", "differentiator", "goal"],
                "keywords": ["product strategy", "platform", "app", "audience", "gap"],
                "why_it_works": [
                    "Anchors the prompt to a real user problem.",
                    "Makes differentiation explicit.",
                    "Produces a more actionable product direction.",
                ],
                "prompt_text": (
                    "Create a product strategy brief for [product]. "
                    "Target audience: [audience]. Core pain point: [pain_point]. "
                    "Differentiator: [differentiator]. Goal: [goal]. "
                    "Return positioning, user promise, feature priorities, risks, and next strategic steps."
                ),
            },
            {
                "id": "product-strategy-mvp",
                "title": "MVP Scope Builder",
                "subcategory": "MVP Planning",
                "summary": "Turn an early-stage idea into a focused MVP planning prompt.",
                "template_fields": ["product", "audience", "must_have_features", "timeframe", "goal"],
                "keywords": ["mvp", "scope", "feature priorities", "launch"],
                "why_it_works": [
                    "Forces the idea into a smaller launchable version.",
                    "Adds user and time constraints.",
                    "Prevents feature sprawl.",
                ],
                "prompt_text": (
                    "Define an MVP plan for [product]. "
                    "Audience: [audience]. Must-have features: [must_have_features]. "
                    "Timeframe: [timeframe]. Goal: [goal]. "
                    "Return MVP scope, what to exclude, launch assumptions, and a simple execution sequence."
                ),
            },
            {
                "id": "product-strategy-positioning",
                "title": "Positioning Angle Builder",
                "subcategory": "Positioning",
                "summary": "Turn a rough product idea into a sharper positioning prompt.",
                "template_fields": ["product", "audience", "market_gap", "competitors", "goal"],
                "keywords": ["positioning", "market gap", "competitors", "messaging"],
                "why_it_works": [
                    "Adds market context to the prompt.",
                    "Pushes the model toward clearer differentiation.",
                    "Useful for messaging and strategy together.",
                ],
                "prompt_text": (
                    "Sharpen the positioning for [product]. "
                    "Audience: [audience]. Market gap: [market_gap]. Competitors or alternatives: [competitors]. "
                    "Goal: [goal]. Return positioning statement, audience-specific value, proof points, and messaging angles."
                ),
            },
        ],
    },
    {
        "category": "Business & Strategy",
        "pack": "Business Idea Validation Pack",
        "domain": "Business",
        "interest": "Founders",
        "use_case": "Stress-test a startup or business concept before building it.",
        "keywords": [
            "business",
            "startup",
            "market",
            "validate",
            "idea",
            "opportunity",
            "demand",
            "market gap",
            "competitive",
            "research",
        ],
        "common_missing_elements": ["target user", "problem worth solving", "validation goal", "decision criteria"],
        "repair_hints": [
            "Ask what needs to be proven before building.",
            "State the market gap or unmet need the idea is trying to solve.",
            "Add the decision criteria so the output leads to a real go/no-go judgment.",
        ],
        "templates": [
            {
                "id": "business-idea-validation",
                "title": "Business Idea Validator",
                "subcategory": "Idea Validation",
                "summary": "Turn a startup idea into a validation-focused research prompt.",
                "template_fields": ["topic", "audience", "pain_point", "decision_goal", "criteria"],
                "keywords": ["idea validation", "market demand", "startup research"],
                "why_it_works": [
                    "Focuses the prompt on evidence instead of hype.",
                    "Adds decision criteria for clearer output.",
                    "Useful before investing time in the build.",
                ],
                "prompt_text": (
                    "Evaluate this business idea: [topic]. "
                    "Audience: [audience]. Pain point: [pain_point]. "
                    "Decision goal: [decision_goal]. Criteria: [criteria]. "
                    "Return demand signals, market risks, differentiation, and a go/no-go recommendation with reasons."
                ),
            },
            {
                "id": "business-idea-gap-analysis",
                "title": "Market Gap Analyzer",
                "subcategory": "Gap Analysis",
                "summary": "Turn a rough market observation into a sharper gap-analysis prompt.",
                "template_fields": ["topic", "audience", "market_gap", "competitors", "goal"],
                "keywords": ["market gap", "competitive", "opportunity", "white space"],
                "why_it_works": [
                    "Anchors the prompt in a specific opportunity gap.",
                    "Adds competitors and target audience.",
                    "Improves strategic usefulness.",
                ],
                "prompt_text": (
                    "Analyze the market opportunity for [topic]. "
                    "Target audience: [audience]. Suspected gap: [market_gap]. "
                    "Current competitors or alternatives: [competitors]. Goal: [goal]. "
                    "Return underserved needs, why incumbents miss them, and promising product angles."
                ),
            },
            {
                "id": "business-idea-research-brief",
                "title": "Founder Research Brief",
                "subcategory": "Research Briefs",
                "summary": "Create a founder-style research brief to guide product decisions.",
                "template_fields": ["topic", "audience", "focus_area", "goal", "format"],
                "keywords": ["research brief", "founder", "strategy", "market research"],
                "why_it_works": [
                    "Turns vague curiosity into a focused research brief.",
                    "Adds audience and focus area.",
                    "Makes the output easier to act on.",
                ],
                "prompt_text": (
                    "Build a research brief on [topic]. "
                    "Audience: [audience]. Focus area: [focus_area]. Goal: [goal]. "
                    "Return the result in [format] with key findings, implications, risks, and next questions."
                ),
            },
        ],
    },
    {
        "category": "Business & Strategy",
        "pack": "Proposal Pack",
        "domain": "Business",
        "interest": "Founders",
        "use_case": "Turn a vague business ask into a decision-ready proposal.",
        "keywords": ["proposal", "scope", "deliverables", "client", "plan", "offer"],
        "common_missing_elements": ["decision goal", "audience", "scope", "success criteria"],
        "repair_hints": [
            "Say what decision the proposal should unlock.",
            "List the deliverables or scope so the model can stay concrete.",
            "Add success criteria or timeline so the proposal feels real.",
        ],
        "templates": [
            {
                "id": "proposal-client-scope",
                "title": "Client Proposal Builder",
                "subcategory": "Client Proposals",
                "summary": "Create a proposal with scope, timeline, and next steps.",
                "template_fields": ["service", "client_type", "deliverables", "timeline", "cta"],
                "keywords": ["client proposal", "scope", "timeline", "deliverables"],
                "why_it_works": [
                    "Forces scope clarity.",
                    "Adds timeline and CTA.",
                    "Reduces vague business language.",
                ],
                "prompt_text": (
                    "Create a client proposal for [service] for [client_type]. "
                    "Deliverables include [deliverables]. Timeline is [timeline]. "
                    "Return sections for problem, proposed solution, deliverables, timeline, pricing placeholder, and a CTA to [cta]."
                ),
            },
            {
                "id": "proposal-internal-initiative",
                "title": "Internal Initiative Proposal",
                "subcategory": "Internal Proposals",
                "summary": "Propose an internal project with rationale, risk, and expected outcome.",
                "template_fields": ["initiative", "stakeholders", "expected_outcome", "risks", "timeline"],
                "keywords": ["internal proposal", "initiative", "stakeholders", "approval"],
                "why_it_works": [
                    "Clarifies the expected outcome.",
                    "Makes risks and stakeholders explicit.",
                    "Improves decision-readiness.",
                ],
                "prompt_text": (
                    "Write an internal proposal for [initiative]. "
                    "Stakeholders: [stakeholders]. Expected outcome: [expected_outcome]. "
                    "Key risks: [risks]. Timeline: [timeline]. Return a concise executive-style proposal."
                ),
            },
            {
                "id": "proposal-pricing-rationale",
                "title": "Pricing Proposal Framer",
                "subcategory": "Pricing Proposals",
                "summary": "Frame a proposal around value and scope instead of raw pricing.",
                "template_fields": ["offer", "audience", "value_case", "pricing_model", "cta"],
                "keywords": ["pricing", "offer", "value", "proposal"],
                "why_it_works": [
                    "Shifts the prompt toward value framing.",
                    "Adds audience and pricing model.",
                    "Improves persuasive structure.",
                ],
                "prompt_text": (
                    "Write a pricing proposal for [offer] for [audience]. "
                    "The value case is [value_case]. Use a [pricing_model] model. "
                    "Return sections for value, scope, pricing logic, objections, and CTA to [cta]."
                ),
            },
        ],
    },
    {
        "category": "Business & Strategy",
        "pack": "Meeting Summary Pack",
        "domain": "Business",
        "interest": "Operators",
        "use_case": "Convert messy notes into useful summaries and action plans.",
        "keywords": ["meeting", "notes", "summary", "actions", "decisions", "follow-up"],
        "common_missing_elements": ["participants", "goal", "decisions", "next steps"],
        "repair_hints": [
            "Name the purpose of the meeting before asking for a summary.",
            "Ask for decisions and action items separately so nothing gets buried.",
            "Include who owns each next step if possible.",
        ],
        "templates": [
            {
                "id": "meeting-summary-exec",
                "title": "Executive Meeting Summary",
                "subcategory": "Executive Summaries",
                "summary": "Summarize a meeting into decisions, risks, and next steps.",
                "template_fields": ["meeting_goal", "stakeholders", "key_topics", "next_step_owner"],
                "keywords": ["executive summary", "decisions", "meeting"],
                "why_it_works": [
                    "Separates decisions from discussion.",
                    "Improves scan-ability for busy readers.",
                    "Adds accountability for next steps.",
                ],
                "prompt_text": (
                    "Summarize meeting notes for a meeting whose goal was [meeting_goal]. "
                    "Stakeholders: [stakeholders]. Key topics: [key_topics]. "
                    "Return sections for summary, decisions, blockers, and next steps with owner [next_step_owner] where possible."
                ),
            },
            {
                "id": "meeting-summary-client-call",
                "title": "Client Call Recap",
                "subcategory": "Client Recaps",
                "summary": "Turn a client call into a clear recap and follow-up note.",
                "template_fields": ["client_name", "call_goal", "agreed_points", "follow_up"],
                "keywords": ["client call", "recap", "follow-up", "agreement"],
                "why_it_works": [
                    "Makes agreements explicit.",
                    "Creates a reusable recap format.",
                    "Helps reduce missed follow-ups.",
                ],
                "prompt_text": (
                    "Create a recap for a call with [client_name]. "
                    "The goal was [call_goal]. Agreed points: [agreed_points]. "
                    "Return a concise recap with summary, agreed actions, open questions, and follow-up needed: [follow_up]."
                ),
            },
            {
                "id": "meeting-summary-standup",
                "title": "Team Standup Digest",
                "subcategory": "Standups",
                "summary": "Compress standup updates into blockers, wins, and next actions.",
                "template_fields": ["team_name", "update_scope", "blockers", "next_steps"],
                "keywords": ["standup", "team update", "blockers"],
                "why_it_works": [
                    "Pulls out blockers quickly.",
                    "Prevents updates from staying too vague.",
                    "Adds action focus to routine notes.",
                ],
                "prompt_text": (
                    "Summarize a standup for [team_name]. "
                    "The update scope is [update_scope]. Known blockers: [blockers]. "
                    "Return wins, blockers, owner-specific next steps, and a short team summary."
                ),
            },
        ],
    },
    {
        "category": "Coding & Technical",
        "pack": "Code Explainer Pack",
        "domain": "Coding",
        "interest": "Builders",
        "use_case": "Explain code clearly for debugging, onboarding, or learning.",
        "keywords": ["code", "function", "python", "javascript", "explain", "snippet"],
        "common_missing_elements": ["language", "audience", "depth", "goal"],
        "repair_hints": [
            "Name the language and framework so the explanation can be accurate.",
            "Say who the explanation is for: beginner, peer, or senior reviewer.",
            "Ask for step-by-step or line-by-line if you want deeper help.",
        ],
        "templates": [
            {
                "id": "code-explainer-junior",
                "title": "Junior-Friendly Code Explainer",
                "subcategory": "Beginner Explainers",
                "summary": "Explain code in plain English for a junior developer.",
                "template_fields": ["language", "code_goal", "audience", "format"],
                "keywords": ["junior developer", "line by line", "explain code"],
                "why_it_works": [
                    "Makes the audience explicit.",
                    "Improves explanation depth.",
                    "Prevents overly advanced jargon.",
                ],
                "prompt_text": (
                    "Explain this [language] code for [audience]. "
                    "The code is trying to [code_goal]. "
                    "Return the explanation in [format], and include line-by-line notes plus the main concept behind it."
                ),
            },
            {
                "id": "code-explainer-review",
                "title": "Code Review Explainer",
                "subcategory": "Peer Reviews",
                "summary": "Turn code into a review-style explanation with risks and improvements.",
                "template_fields": ["language", "context", "main_risk", "focus_area"],
                "keywords": ["review", "risk", "improvement", "refactor"],
                "why_it_works": [
                    "Adds review focus instead of generic explanation.",
                    "Encourages concrete risk spotting.",
                    "Makes the output more actionable.",
                ],
                "prompt_text": (
                    "Review and explain this [language] code. "
                    "Context: [context]. Focus area: [focus_area]. Main risk to watch: [main_risk]. "
                    "Return what the code does, what is risky, and what could be improved."
                ),
            },
            {
                "id": "code-explainer-architecture",
                "title": "Architecture Walkthrough Prompt",
                "subcategory": "Architecture Walkthroughs",
                "summary": "Explain code in terms of flow, modules, and system impact.",
                "template_fields": ["language", "system_goal", "components", "audience"],
                "keywords": ["architecture", "module", "flow", "system"],
                "why_it_works": [
                    "Pulls the explanation up to system level.",
                    "Useful for onboarding and handoffs.",
                    "Adds components and audience context.",
                ],
                "prompt_text": (
                    "Explain this [language] code as part of a larger system. "
                    "System goal: [system_goal]. Key components: [components]. Audience: [audience]. "
                    "Return flow overview, module responsibilities, dependencies, and key caveats."
                ),
            },
        ],
    },
    {
        "category": "Coding & Technical",
        "pack": "Bug Fix Pack",
        "domain": "Coding",
        "interest": "Builders",
        "use_case": "Turn a vague bug report into a safer debugging prompt.",
        "keywords": ["bug", "fix", "error", "issue", "traceback", "broken", "debug"],
        "common_missing_elements": ["reproduction", "expected behavior", "actual behavior", "environment"],
        "repair_hints": [
            "Describe what should have happened and what actually happened.",
            "Add the environment or stack details when possible.",
            "Include reproduction steps so the fix stays grounded.",
        ],
        "templates": [
            {
                "id": "bug-fix-root-cause",
                "title": "Root Cause Debugger",
                "subcategory": "Root Cause Analysis",
                "summary": "Structure a bug prompt around symptoms, repro, and likely causes.",
                "template_fields": ["stack", "symptom", "expected_behavior", "repro_steps"],
                "keywords": ["root cause", "repro", "symptom", "expected behavior"],
                "why_it_works": [
                    "Prevents jumping straight to patching.",
                    "Improves bug clarity.",
                    "Encourages verification steps.",
                ],
                "prompt_text": (
                    "Investigate a bug in [stack]. "
                    "Symptom: [symptom]. Expected behavior: [expected_behavior]. Reproduction steps: [repro_steps]. "
                    "Return likely causes, debugging plan, patch idea, and verification steps."
                ),
            },
            {
                "id": "bug-fix-regression-check",
                "title": "Regression-Safe Fix Planner",
                "subcategory": "Regression Checks",
                "summary": "Generate a safer fix prompt that includes tests and rollback thinking.",
                "template_fields": ["stack", "bug_summary", "risky_area", "test_focus"],
                "keywords": ["regression", "tests", "rollback", "safe fix"],
                "why_it_works": [
                    "Adds regression awareness.",
                    "Forces test planning.",
                    "Reduces risky one-shot fixes.",
                ],
                "prompt_text": (
                    "Plan a safe bug fix in [stack]. "
                    "Bug summary: [bug_summary]. Risky area: [risky_area]. Test focus: [test_focus]. "
                    "Return likely cause, minimal patch strategy, regression risks, tests, and rollback notes."
                ),
            },
            {
                "id": "bug-fix-ticket-breakdown",
                "title": "Bug Ticket Breakdown",
                "subcategory": "Ticket Breakdown",
                "summary": "Turn a bug report into an implementable engineering ticket.",
                "template_fields": ["system_area", "symptom", "environment", "done_definition"],
                "keywords": ["ticket", "engineering task", "done definition"],
                "why_it_works": [
                    "Makes bug prompts implementation-ready.",
                    "Clarifies environment and completion criteria.",
                    "Useful for handoff to engineers.",
                ],
                "prompt_text": (
                    "Turn this bug into an engineering task for [system_area]. "
                    "Symptom: [symptom]. Environment: [environment]. Done definition: [done_definition]. "
                    "Return the problem, acceptance criteria, likely cause, fix plan, and testing notes."
                ),
            },
        ],
    },
    {
        "category": "Learning & Research",
        "pack": "Study Guide Pack",
        "domain": "Education",
        "interest": "Students",
        "use_case": "Convert a topic into a study aid with structure and retention support.",
        "keywords": ["study", "guide", "exam", "revision", "concept", "learn"],
        "common_missing_elements": ["difficulty level", "goal", "format", "time limit"],
        "repair_hints": [
            "Say whether this is for beginner, intermediate, or exam-level study.",
            "Ask for examples or quiz questions if you want better retention.",
            "Add time pressure if the study output needs to be concise.",
        ],
        "templates": [
            {
                "id": "study-guide-beginner",
                "title": "Beginner Study Guide Builder",
                "subcategory": "Study Guides",
                "summary": "Create a beginner-friendly study guide with examples and recap.",
                "template_fields": ["topic", "level", "goal", "format"],
                "keywords": ["study guide", "beginner", "examples", "recap"],
                "why_it_works": [
                    "Makes the learning level explicit.",
                    "Adds recap and examples.",
                    "Creates a reusable study format.",
                ],
                "prompt_text": (
                    "Create a study guide about [topic] for a [level] learner. "
                    "The goal is [goal]. Return the guide in [format] with explanation, examples, recap, and 5 review questions."
                ),
            },
            {
                "id": "study-guide-exam-sprint",
                "title": "Exam Revision Sprint",
                "subcategory": "Revision Plans",
                "summary": "Turn a topic list into a fast revision prompt.",
                "template_fields": ["topics", "exam_date", "weak_areas", "time_available"],
                "keywords": ["exam", "revision", "weak areas", "time available"],
                "why_it_works": [
                    "Adds urgency and prioritization.",
                    "Focuses on weak areas instead of generic study.",
                    "Builds a realistic plan.",
                ],
                "prompt_text": (
                    "Create a revision sprint for these topics: [topics]. "
                    "Exam date: [exam_date]. Weak areas: [weak_areas]. Time available: [time_available]. "
                    "Return a priority order, daily study blocks, recall tasks, and practice prompts."
                ),
            },
            {
                "id": "study-guide-concept-explainer",
                "title": "Concept Explainer Prompt",
                "subcategory": "Concept Explainability",
                "summary": "Explain a concept simply, then deepen it with examples and analogies.",
                "template_fields": ["concept", "audience", "example_type", "format"],
                "keywords": ["concept", "analogy", "explain simply", "examples"],
                "why_it_works": [
                    "Improves conceptual clarity.",
                    "Adds examples and analogy anchors.",
                    "Makes learning less abstract.",
                ],
                "prompt_text": (
                    "Explain [concept] for [audience]. "
                    "Use [example_type] examples and return it in [format]. "
                    "Start simple, then deepen the explanation, and end with a short self-test."
                ),
            },
        ],
    },
    {
        "category": "Learning & Research",
        "pack": "Paper Summary Pack",
        "domain": "Education",
        "interest": "Researchers",
        "use_case": "Turn dense papers or notes into useful summaries.",
        "keywords": ["paper", "research", "summary", "abstract", "methods", "results"],
        "common_missing_elements": ["goal", "audience", "summary format", "focus area"],
        "repair_hints": [
            "Say whether you care more about methods, results, or implications.",
            "Name the audience so the summary is pitched correctly.",
            "Ask for bullets, table, or plain-language output explicitly.",
        ],
        "templates": [
            {
                "id": "paper-summary-plain-language",
                "title": "Plain-Language Paper Summary",
                "subcategory": "Accessible Summaries",
                "summary": "Summarize a paper in simple language with methods and results.",
                "template_fields": ["paper_topic", "audience", "focus_area", "format"],
                "keywords": ["plain language", "paper summary", "methods", "results"],
                "why_it_works": [
                    "Makes the audience explicit.",
                    "Avoids jargon overload.",
                    "Improves practical usefulness of summaries.",
                ],
                "prompt_text": (
                    "Summarize a research paper about [paper_topic] for [audience]. "
                    "Focus mainly on [focus_area]. Return the summary in [format] with problem, method, findings, limitations, and practical takeaway."
                ),
            },
            {
                "id": "paper-summary-comparison",
                "title": "Paper Comparison Prompt",
                "subcategory": "Paper Comparisons",
                "summary": "Compare papers by approach, results, and limitations.",
                "template_fields": ["paper_set", "comparison_goal", "audience", "format"],
                "keywords": ["compare papers", "research comparison", "limitations"],
                "why_it_works": [
                    "Adds a comparison goal so the output has purpose.",
                    "Makes tradeoffs explicit.",
                    "Improves research synthesis quality.",
                ],
                "prompt_text": (
                    "Compare these papers: [paper_set]. "
                    "Comparison goal: [comparison_goal]. Audience: [audience]. "
                    "Return the result in [format] with methodology differences, strengths, weaknesses, and recommendation."
                ),
            },
            {
                "id": "paper-summary-lit-review",
                "title": "Literature Review Starter",
                "subcategory": "Literature Reviews",
                "summary": "Turn notes into an early-stage lit review structure.",
                "template_fields": ["topic", "sources", "themes", "research_gap"],
                "keywords": ["literature review", "themes", "research gap"],
                "why_it_works": [
                    "Creates thematic structure.",
                    "Highlights research gaps.",
                    "Turns notes into a usable review format.",
                ],
                "prompt_text": (
                    "Build a literature review starter on [topic]. "
                    "Sources: [sources]. Themes already identified: [themes]. Suspected research gap: [research_gap]. "
                    "Return key themes, contradictions, gaps, and next reading directions."
                ),
            },
        ],
    },
    {
        "category": "Creative & General",
        "pack": "Story Idea Pack",
        "domain": "Creative",
        "interest": "Creators",
        "use_case": "Turn a loose creative idea into a more directed prompt.",
        "keywords": ["story", "character", "plot", "scene", "creative writing", "fiction"],
        "common_missing_elements": ["genre", "tone", "stakes", "character goal"],
        "repair_hints": [
            "Name the genre so the style stops drifting.",
            "Add the character goal or conflict to raise stakes.",
            "Clarify whether you want an outline, a scene, or a full draft.",
        ],
        "templates": [
            {
                "id": "story-idea-outline",
                "title": "Story Outline Builder",
                "subcategory": "Story Outlines",
                "summary": "Turn a story concept into an outline with conflict and resolution.",
                "template_fields": ["premise", "genre", "protagonist", "stakes", "ending_type"],
                "keywords": ["story outline", "genre", "stakes", "premise"],
                "why_it_works": [
                    "Adds structure and narrative stakes.",
                    "Prevents generic creative writing output.",
                    "Clarifies the intended ending type.",
                ],
                "prompt_text": (
                    "Create a story outline from this premise: [premise]. "
                    "Genre: [genre]. Protagonist: [protagonist]. Stakes: [stakes]. Ending type: [ending_type]. "
                    "Return setup, inciting incident, conflict, climax, and ending."
                ),
            },
            {
                "id": "story-idea-character-builder",
                "title": "Character Prompt Builder",
                "subcategory": "Character Design",
                "summary": "Create a richer character prompt with motive, flaw, and tension.",
                "template_fields": ["character_type", "goal", "flaw", "setting", "tone"],
                "keywords": ["character", "backstory", "goal", "flaw"],
                "why_it_works": [
                    "Forces clearer character motivation.",
                    "Adds flaw and tension.",
                    "Improves scene consistency later.",
                ],
                "prompt_text": (
                    "Design a [character_type] character. "
                    "Main goal: [goal]. Major flaw: [flaw]. Setting: [setting]. Tone: [tone]. "
                    "Return backstory, motive, contradiction, and a scene hook."
                ),
            },
            {
                "id": "story-idea-scene-writer",
                "title": "Scene Writing Prompt",
                "subcategory": "Scene Drafts",
                "summary": "Build a scene prompt with tension, objective, and payoff.",
                "template_fields": ["scene_goal", "characters", "setting", "conflict", "tone"],
                "keywords": ["scene", "dialogue", "conflict", "tension"],
                "why_it_works": [
                    "Makes the scene objective explicit.",
                    "Adds tension so the scene is not flat.",
                    "Improves consistency of tone and setting.",
                ],
                "prompt_text": (
                    "Write a scene where [characters] are in [setting]. "
                    "The scene goal is [scene_goal]. The core conflict is [conflict]. Tone: [tone]. "
                    "Return a scene with tension, clear beats, and a small payoff."
                ),
            },
        ],
    },
    {
        "category": "Creative & General",
        "pack": "General Prompt Repair Pack",
        "domain": "General",
        "interest": "General",
        "use_case": "Repair vague prompts when no domain-specific pack is obvious.",
        "keywords": ["improve prompt", "better prompt", "rewrite", "clarify", "general"],
        "common_missing_elements": ["goal", "audience", "format", "constraints"],
        "repair_hints": [
            "State what a strong answer should help the reader do.",
            "Name the likely audience or decision-maker.",
            "Add an output format and one or two constraints.",
        ],
        "templates": [
            {
                "id": "general-repair-basic",
                "title": "General Prompt Clarifier",
                "subcategory": "Prompt Repair",
                "summary": "Turn a vague idea into a structured task, context, and output request.",
                "template_fields": ["task", "audience", "goal", "format", "constraints"],
                "keywords": ["clarify", "repair", "general prompt", "structure"],
                "why_it_works": [
                    "Adds the core missing fields most prompts lack.",
                    "Creates a reusable prompt skeleton.",
                    "Improves output consistency fast.",
                ],
                "prompt_text": (
                    "Improve this prompt: [task]. "
                    "Audience: [audience]. Goal: [goal]. Output format: [format]. Constraints: [constraints]. "
                    "Return a structured prompt with task, context, requirements, and output format."
                ),
            },
            {
                "id": "general-repair-decision",
                "title": "Decision-Making Prompt Builder",
                "subcategory": "Decision Support",
                "summary": "Improve a prompt so it leads to a clearer decision or recommendation.",
                "template_fields": ["topic", "decision_goal", "audience", "criteria", "format"],
                "keywords": ["decision", "recommendation", "criteria", "options"],
                "why_it_works": [
                    "Adds criteria for stronger outputs.",
                    "Focuses the prompt on a decision instead of generic analysis.",
                    "Makes the result easier to act on.",
                ],
                "prompt_text": (
                    "Create a stronger prompt about [topic]. "
                    "The decision goal is [decision_goal]. Audience: [audience]. Criteria: [criteria]. "
                    "Return the answer in [format] and make tradeoffs explicit."
                ),
            },
            {
                "id": "general-repair-step-plan",
                "title": "Step-by-Step Plan Builder",
                "subcategory": "Execution Planning",
                "summary": "Turn a rough ask into a concrete step-by-step plan prompt.",
                "template_fields": ["task", "goal", "timeframe", "constraints", "format"],
                "keywords": ["plan", "steps", "execution", "roadmap"],
                "why_it_works": [
                    "Adds timeframe and constraints.",
                    "Improves structure for action-oriented prompts.",
                    "Useful across many categories.",
                ],
                "prompt_text": (
                    "Turn this rough ask into a planning prompt: [task]. "
                    "Goal: [goal]. Timeframe: [timeframe]. Constraints: [constraints]. "
                    "Return a [format] plan with steps, risks, and next actions."
                ),
            },
        ],
    },
]
