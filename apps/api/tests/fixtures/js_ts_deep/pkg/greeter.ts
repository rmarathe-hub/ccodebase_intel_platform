/** Default-export greeter used across modules. */
export default class Greeter {
  hello(): string {
    return "hi";
  }
}

export function helper(): string {
  return "foreign";
}
