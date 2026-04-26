import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatCard } from "@/components/atoms/stats/stat-card";
import { renderWithProviders } from "../../../helpers/render";

describe("StatCard", () => {
  it("should display the label", () => {
    renderWithProviders(<StatCard label="Total Users" value={42} />);
    expect(screen.getByText("Total Users")).toBeInTheDocument();
  });

  it("should display the value", () => {
    renderWithProviders(<StatCard label="Total Users" value={42} />);
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("should display the unit when provided", () => {
    renderWithProviders(<StatCard label="Success Rate" value="98.5" unit="%" />);
    expect(screen.getByText("%")).toBeInTheDocument();
  });

  it("should not display a unit element when unit is not provided", () => {
    renderWithProviders(<StatCard label="Total Users" value={42} />);
    expect(screen.queryByText("%")).not.toBeInTheDocument();
  });
});
