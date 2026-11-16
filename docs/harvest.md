# Historical provenance and generalized engineering lessons

This is historical evidence of the legacy workspace bootstrap, not an active
project registry or set of product requirements. The migration retires imported
client assumptions without deleting original repositories, notes or recovery data.

| Historical source | Reusable lesson | Current generic home |
|---|---|---|
| AMG / WorkMerit environment examples | Keep names separate from secrets; configuration belongs to the product | Product-local environment templates; control template has no product variables |
| AMG / WorkMerit UI and assessment guidance | Respect design tokens, bidirectional UX when required, and trusted server decisions | AGENTS.md project isolation guidance |
| HR Odoo / HRA framework notes | Check installed, version-matched framework documentation | Optional directives/nextjs-verification.md |
| Legacy repository without a remote | Review backup and recovery before changes; a remote alone is insufficient | governance/SECURITY_AND_APPROVALS.md |
| Per-harness instruction pointers | Maintain one canonical policy with project-local pointers | CLAUDE.md, GEMINI.md and projects/_template/ |

Legacy stack versions, payment integrations, hosting choices, repository URLs and
client-specific constraints are not factory defaults. The dated bootstrap log is
retained unchanged as historical evidence. The audit reports this exact provenance
file and that log as history; new files and active guidance are not exempt.
