// Step 0 placeholder for API functions whose backend lands on a feature branch.
// Each stub is a typed const, so callers compile against the final signature today; the owner swaps the
// right-hand side for a real apiFetch call (see docs/api.md §13–§17).
export function notImplemented(name: string): () => Promise<never> {
  return () => Promise.reject(new Error(`${name} is not implemented yet (Step 0 stub, see docs/api.md)`));
}
