import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StreamingIndicator } from "@/components/molecules/chat/streaming-indicator";
import { renderWithProviders } from "../../../helpers/render";

describe("StreamingIndicator", () => {
  it("should render three animated dots", () => {
    renderWithProviders(<StreamingIndicator />);
    expect(screen.getAllByRole("presentation")).toHaveLength(3);
  });

  it("should render the thinking label", () => {
    renderWithProviders(<StreamingIndicator />);
    expect(screen.getByText(/thinking/i)).toBeInTheDocument();
  });
});
