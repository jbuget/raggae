import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StreamingDot } from "@/components/atoms/chat/streaming-dot";
import { renderWithProviders } from "../../../helpers/render";

describe("StreamingDot", () => {
  it("should render a dot element", () => {
    renderWithProviders(<StreamingDot delay={0} />);
    const dot = screen.getByRole("presentation");
    expect(dot).toBeInTheDocument();
  });

  it("should apply bounce animation class", () => {
    renderWithProviders(<StreamingDot delay={0} />);
    expect(screen.getByRole("presentation")).toHaveClass("animate-bounce");
  });

  it("should apply the given animation delay as inline style", () => {
    renderWithProviders(<StreamingDot delay={150} />);
    expect(screen.getByRole("presentation")).toHaveStyle({ animationDelay: "150ms" });
  });
});
