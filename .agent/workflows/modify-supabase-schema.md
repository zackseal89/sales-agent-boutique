---
description: Safely update schema using MCP without corrupting data.
---

-Read current schema via MCP inspection.

-Identify unused / broken / conflicting tables or fields.

-Propose schema changes before executing.

-Create SQL migration steps (not direct destructive edits).

-Apply changes in this order:

-New tables/fields

-Migrations

-Deletions (only if confirmed safe)

-Validate relationships and constraints.

-Output: final schema diagram + change log.

Guardrails:

-Never drop tables with data before backup.

-Avoid renaming critical columns unless migration is clear.