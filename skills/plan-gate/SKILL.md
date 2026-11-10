---
name: plan-gate
description: Use before starting ANY task that involves more than one edit, file, or step - coding, refactoring, writing, configuration, migrations. Forces a short written plan (goal, unknowns, success criteria, step order) BEFORE the first change. Do not use for single-line fixes or pure questions.
---

# plan-gate: no edits until the plan exists

The most expensive failure mode in agentic work is not a wrong answer. It is discovering the real shape of the task halfway through changing things. This skill makes that discovery happen BEFORE anything changes, when it costs nothing.

## The gate

Before your first edit, write a plan in your response. Not in your head. Written, visible, in this exact shape:

```
GOAL: <one sentence: what is true when this is done>
UNKNOWNS: <what you have not verified yet - each with how you will verify it>
SUCCESS CRITERIA: <how you and the user will KNOW it worked - a command, a test, an observable>
STEPS: <numbered, smallest useful granularity, verification steps included>
OUT OF SCOPE: <adjacent things you noticed but will NOT touch>
```

Rules:
1. **The plan comes from evidence, not memory.** Read the relevant files and run the relevant read-only commands FIRST. A plan written before looking is a guess with formatting.
2. **Every unknown gets a verification step.** "Probably X" is not a plan line. "Check whether X by doing Y" is.
3. **Success criteria must be executable.** "Code works" fails this test. "npm test passes and GET /health returns 200" passes it.
4. **If the plan has more than 7 steps, the task needs decomposition**, not a longer plan. Split it and gate each part.
5. **When reality contradicts the plan mid-task, STOP and re-plan.** Do not improvise past a surprise. A surprised plan is an invalid plan. State what changed, update the plan, then continue.

## What this catches

- The hidden dependency you would have found at step 4 with three files already half-edited.
- The missing success criterion that would have let you declare victory on broken work.
- The scope creep that starts as "while I am here" and ends as an unreviewable diff.

## Anti-patterns this skill exists to kill

- Diving in: first tool call is an edit.
- The mental plan: "I know what to do" followed by discovering you did not.
- The pivot cascade: three abandoned half-approaches in one session because none was planned.

## Resuming Prior Planned Work

When the user says "I asked you [before] to..." or references prior planned work, this is a PLAN-RESUME event, not a fresh investigation. The user expects you to FOLLOW a plan that already exists.

**MANDATORY workflow:**
1. **Search for the plan FIRST.** Before touching ANY file or running ANY diagnostic, search:
   - `~/.hermes/plans/` for markdown files matching the topic
   - the sandboxed plans directory, if one is configured
   - the project knowledge base for the topic + "plan"
   - `session_search` for the prior session where the plan was discussed
2. **If found:** Read it completely. The plan may specify a different architecture, database, or approach than what's currently on disk. Follow the plan, don't improvise.
3. **If NOT found after exhaustive search:** Ask the user. "I searched [locations] but can't find the plan for X. Where is it?" Do NOT start investigating the current state or improvising fixes while the plan is missing.

**Anti-pattern this catches:** You dive into investigating a JSON state file when the plan specifies Postgres. You refactor a component when the plan says to delete it. The user says "did you even look for the plan" because you treated a plan-resume as a fresh debug session.

## Exception

Trivial tasks (one obvious edit, zero unknowns) may skip the written plan. Say "trivial, skipping plan-gate" so the skip is a decision, not a lapse. If you are wrong about it being trivial, the moment you notice is the moment you stop and write the plan.
