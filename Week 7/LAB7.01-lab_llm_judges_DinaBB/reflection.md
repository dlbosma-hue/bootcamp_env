# Reflection
## Client Scenario: Healthcare - Patient Record Summarization

---

## Question 1: What would change if the client's data was in French?

Honestly, a lot would get harder really fast. The biggest headache would be finding benchmarks — pretty much all the standard medical NLP datasets (MedQA, MIMIC-III stuff) are in English. So we'd either have to track down a French clinical dataset (they exist, but they're way more locked down than English ones) or just build a test set ourselves from scratch using actual de-identified French records. Neither option is fun.

And it's not just the data problem. Even our rule-based checks would need a rework — French medical terminology doesn't always translate directly. Like "insuffisance cardiaque" for heart failure, or the way French clinical notes handle medication abbreviations differently. The LLM judge we pick would also need to genuinely be good at French clinical language, not just "can hold a conversation in French" level.

There's also this sneaky issue I hadn't really thought about before: most big LLMs are trained way more on English than anything else. So even if a model seems fluent in French, its reasoning and clinical accuracy might quietly degrade when you push it into specialist medical territory. That's not something you'd catch without carefully designed eval and probably some native French-speaking clinicians in the loop.

---

## Question 2: How would you respond if the client asked "Is this model AGI-level?"

Short answer: I'd tell them that's not really a question our eval can answer — and honestly, nobody's eval can answer it right now because "AGI-level" doesn't have an agreed-upon definition yet.

The more useful reframe for the client is: instead of asking if it's AGI, ask if it's good enough for *this specific task* under *these specific conditions*. That's something we can measure.

If someone really wanted to probe AGI-style capabilities, you'd need to go way beyond summarization accuracy. You'd want to test things like: can it reason through contradictory findings? Can it handle totally unfamiliar scenarios with no examples to lean on? Does it know when it doesn't know something and flag it? None of that shows up in standard benchmarks.

And even if a model somehow nailed all of that — we'd still need a community-agreed definition of AGI before calling it that. For now, I'd steer the client toward concrete, task-specific metrics and treat any "AGI" talk as more of a marketing thing than something measurable.

---

## Question 3: What is the one thing you could not evaluate without a human?

For me it's the appropriateness of tone in sensitive clinical situations — and Prompt 4 from the lab is a perfect example. That one involved a psychiatric handover note where the patient hadn't consented to family disclosure.

A rule-based check can confirm the consent limitation got mentioned. An LLM judge can scan for stigmatizing language. But neither can really tell you whether a real clinician reading that note at 2am during a shift handover would find it appropriate and useful — or whether it would feel off, overwhelming, or just wrong for the context.

That's the thing about clinical communication: it's not purely factual. There are professional norms, hospital culture, what the receiving nurse needs to know vs. what's just noise — stuff that's learned through years of clinical experience, not text data.

To evaluate this properly, you'd need trained clinical staff (nurses, doctors, clinical educators) going through model outputs with a structured rubric. And that rubric should be built *with* the hospital team, not handed to them, because what "appropriate tone" means can vary by institution. Cutting corners on human eval here isn't just a quality issue — it's a patient safety issue.
