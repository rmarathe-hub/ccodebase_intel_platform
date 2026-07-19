/** Shared frontend helpers. */
export function formatTitle(value: string): string {
  return value.trim().toUpperCase();
}

export function bump(n: number): number {
  return n + 1;
}
