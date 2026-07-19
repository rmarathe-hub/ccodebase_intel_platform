import { util } from "./helpers";
import Greeter from "./greeter";

export interface Point {
  x: number;
  y: number;
}

export type Size = { w: number; h: number };

export function helper(x: number): number {
  return x;
}

export class Service {
  run(): number {
    return helper(1);
  }

  greet(): string {
    return String(this.run());
  }
}

export async function fetchData(): Promise<number> {
  return await util(2);
}

export const load = async (): Promise<number> => {
  await fetchData();
  return helper(3);
};

export function entry(): number {
  Greeter.hello();
  unknownThing(1);
  util(9);
  return helper(0);
}

function ambiguousCaller(): number {
  // helper exists in this module and pkg.greeter — bare name prefers same-module.
  return helper(5);
}
