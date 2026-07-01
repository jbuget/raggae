import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SparklineCard } from "@/components/atoms/stats/sparkline";
import { renderWithProviders } from "../../../helpers/render";

const points = [
  { date: "2026-06-01", value: 10 },
  { date: "2026-06-02", value: 20 },
  { date: "2026-06-03", value: 30 },
];

describe("SparklineCard", () => {
  it("should display the label and the aggregated total", () => {
    renderWithProviders(<SparklineCard label="Messages envoyés" points={points} />);
    expect(screen.getByText("Messages envoyés")).toBeInTheDocument();
    // 10 + 20 + 30 = 60 (fr-FR uses NBSP as thousands separator, none needed here)
    expect(screen.getByText("60")).toBeInTheDocument();
  });

  it("should use the provided total when given", () => {
    renderWithProviders(
      <SparklineCard label="Messages envoyés" points={points} total={999} />,
    );
    expect(screen.getByText("999")).toBeInTheDocument();
  });

  it("should show hover indicator with value and date when the chart is hovered", () => {
    renderWithProviders(<SparklineCard label="Messages envoyés" points={points} />);

    const chart = screen.getByRole("img", { name: /Messages envoyés/i });

    // Simulate hover near the middle point (index 1, value 20)
    fireEvent.mouseMove(chart, { clientX: 150, clientY: 30 });

    // The tooltip should show one of the point values
    // We look for at least one exact value from the dataset
    const hoveredValueVisible =
      screen.queryByText("10") ||
      screen.queryByText("20") ||
      screen.queryByText("30");
    expect(hoveredValueVisible).not.toBeNull();
  });

  it("should hide the hover indicator when mouse leaves the chart", () => {
    renderWithProviders(<SparklineCard label="Messages envoyés" points={points} />);

    const chart = screen.getByRole("img", { name: /Messages envoyés/i });

    fireEvent.mouseMove(chart, { clientX: 150, clientY: 30 });
    fireEvent.mouseLeave(chart);

    // No individual point value should be shown outside of the total (60)
    expect(screen.queryByText("10")).not.toBeInTheDocument();
    expect(screen.queryByText("20")).not.toBeInTheDocument();
    expect(screen.queryByText("30")).not.toBeInTheDocument();
  });
});
