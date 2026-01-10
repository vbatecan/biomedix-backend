---
description: 
---

The Antigravity Integrated Workflow
1.  **Contract Definition:** Define the API using Pydantic models in Python. Generate the OpenAPI spec.
2.  **Type Sync:** Use `openapi-typescript` to generate TypeScript interfaces from the Python backend. This ensures the frontend is never out of sync with API changes.
3.  **Component Scaffolding:**
    * Initialize component state with `signal`.
    * Fetch data using an Angular Service that returns a Signal or an Observable converted via `toSignal()`.
    * Apply `@defer` blocks to all route-level components that are not immediately visible above the fold.
4.  **CI/CD Pipeline:**
    * **Step 1:** Ruff linting & Mypy type check (Python).
    * **Step 2:** Angular Build (with `optimization: true`).
    * **Step 3:** Automated Lighthouse performance audit (Target: 90+ Score).