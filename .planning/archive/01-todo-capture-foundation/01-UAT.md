---
status: testing
phase: 01-todo-capture-foundation
source:
  - .planning/phases/01-todo-capture-foundation/01-01-SUMMARY.md
started: 2026-06-24T21:49:05Z
updated: 2026-06-24T21:49:05Z
---

# Phase 01 UAT

## Current Test

number: 1
name: Capture a pending todo
expected: |
  Create a new pending todo from the canonical template with a title, area, Problem, Solution, Notes, and files list.
  The todo should be saved as a markdown file in `.planning/todos/pending/` with `status: pending` by default.
awaiting: user response

## Tests

### 1. Capture a pending todo

expected: Create a new pending todo from the canonical template with a title, area, Problem, Solution, Notes, and files list. The todo should be saved as a markdown file in `.planning/todos/pending/` with `status: pending` by default.
result: pending

### 2. Reopen preserved todo details

expected: Reopening the saved todo shows the same Problem, Solution, and Notes content unchanged.
result: pending

### 3. Lenient capture warnings do not block saving

expected: If a todo is missing some fields or looks like a probable duplicate, capture still saves the item and shows warnings rather than blocking the save.
result: pending

### 4. Pending queue path is consistent

expected: Newly captured todos appear under `.planning/todos/pending/` with the canonical filename pattern and required frontmatter keys.
result: pending

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps

[none yet]
