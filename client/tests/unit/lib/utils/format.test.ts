import { describe, expect, it } from "vitest";
import { formatDate, formatDateTime, formatFileSize } from "@/lib/utils/format";

describe("formatFileSize", () => {
  it("should format 0 bytes", () => {
    expect(formatFileSize(0)).toBe("0 B");
  });

  it("should format bytes", () => {
    expect(formatFileSize(500)).toBe("500 B");
  });

  it("should format kilobytes", () => {
    expect(formatFileSize(1024)).toBe("1.0 KB");
  });

  it("should format megabytes", () => {
    expect(formatFileSize(1048576)).toBe("1.0 MB");
  });

  it("should format gigabytes", () => {
    expect(formatFileSize(1073741824)).toBe("1.0 GB");
  });

  it("should format fractional sizes", () => {
    expect(formatFileSize(1536)).toBe("1.5 KB");
  });
});

describe("formatDate", () => {
  it("should format a date string", () => {
    const result = formatDate("2026-01-15T10:30:00Z");
    expect(result).toContain("Jan");
    expect(result).toContain("15");
    expect(result).toContain("2026");
  });

  it("should format a Date object", () => {
    const result = formatDate(new Date("2026-06-01T00:00:00Z"));
    expect(result).toContain("2026");
  });
});

describe("formatDateTime", () => {
  it("should include time", () => {
    const result = formatDateTime("2026-01-15T10:30:00Z");
    expect(result).toContain("Jan");
    expect(result).toContain("15");
    expect(result).toContain("2026");
  });
});
