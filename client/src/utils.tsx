export function nullthrows<T>(value: T): NonNullable<T> {
  if (value == null) {
    throw new Error("Expected nonnull");
  }

  return value;
}
