# Directive: Next.js & React 19 Verification SOP

- **Applicability**: Only independently registered projects whose manifests use Next.js. This is an optional stack-specific SOP, not a factory dependency.
- **Goal**: Deterministically verify linting, typechecking, tests, and build boundaries before deploying or creating handover PRs.

---

## Pre-flight Checklist
- [ ] Dependencies installed cleanly via `npm ci` or `pnpm install --frozen-lockfile`.
- [ ] `.env.local` or environment variables set for build preflights.

## Execution Sequence

```powershell
# 1. Typecheck
npm run typecheck # or npx tsc --noEmit

# 2. Lint
npm run lint

# 3. Test Suite
npm test

# 4. Production Build Verification
npm run build
```

## Gotchas & Edge Cases
- **Next.js 16 breaking changes**: Dynamic route parameters in Next.js 15/16 are asynchronous promises. Inspect `node_modules/next/dist/docs/` for breaking routing signatures.
- **Client/Server boundary**: Ensure interactive hooks (`useState`, `useEffect`) are only used in files marked with `'use client'`.
