import { PlayerInfluence } from "./types";

export function nullthrows<T>(value: T): NonNullable<T> {
  if (value == null) {
    throw new Error("Expected nonnull");
  }

  return value;
}

export function titleCase(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1).toLocaleLowerCase())
    .join(" ");
}
