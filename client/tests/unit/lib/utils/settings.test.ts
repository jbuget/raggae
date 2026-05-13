import { describe, expect, it } from "vitest";
import { resolveField, resolveStringField } from "@/lib/utils/settings";

describe("resolveStringField", () => {
  it("returns local value when set", () => {
    expect(resolveStringField("openai", "anthropic")).toBe("openai");
  });

  it("returns 'none' when local is null", () => {
    expect(resolveStringField(null, "anthropic")).toBe("none");
  });

  it("returns 'none' when local is empty string", () => {
    expect(resolveStringField("", "anthropic")).toBe("none");
  });

  it("returns first non-empty chain value when local is undefined", () => {
    expect(resolveStringField(undefined, null, "anthropic")).toBe("anthropic");
  });

  it("returns 'none' when all chain values are absent", () => {
    expect(resolveStringField(undefined, null, undefined)).toBe("none");
  });

  it("returns 'none' when chain is empty", () => {
    expect(resolveStringField(undefined)).toBe("none");
  });

  it("skips null chain values and uses the next one", () => {
    expect(resolveStringField(undefined, null, "cohere")).toBe("cohere");
  });
});

describe("resolveField", () => {
  it("returns local number when set", () => {
    expect(resolveField(5, 8, 10)).toBe(5);
  });

  it("returns null when local is null, ignoring chain", () => {
    expect(resolveField(null, 8, 10)).toBeNull();
  });

  it("returns 0 as a valid local value (not treated as absent)", () => {
    expect(resolveField(0, 8)).toBe(0);
  });

  it("returns false as a valid local value", () => {
    expect(resolveField(false, true)).toBe(false);
  });

  it("returns first non-null chain value when local is undefined", () => {
    expect(resolveField(undefined, null, 8)).toBe(8);
  });

  it("returns null when all chain values are null/undefined", () => {
    expect(resolveField(undefined, null, undefined)).toBeNull();
  });

  it("returns null when chain is empty", () => {
    expect(resolveField(undefined)).toBeNull();
  });

  it("resolves a 4-level chain (local → stored → inherited → system)", () => {
    expect(resolveField(undefined, null, null, 3)).toBe(3);
  });
});
