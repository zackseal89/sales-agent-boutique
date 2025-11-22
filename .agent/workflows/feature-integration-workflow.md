---
description: Integrate a new feature across system layers cleanly.
---

-Identify layers involved: frontend, backend, agent, DB.

-Define integration points clearly.

-Implement in order:

-Backend logic

-Agent updates

-Frontend integration

-Test each layer independently.

-Perform one end-to-end flow test.

-Output: integration map + what changed.

Guardrails:

-No cross-layer assumptions.

-Each layer must work standalone before full integration.