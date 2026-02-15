import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MessageBubble } from "@/components/chat/message-bubble";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("MessageBubble", () => {
  it("should display message content", () => {
    renderWithProviders(
      <MessageBubble role="user" content="Hello world" />,
    );
    expect(screen.getByText("Hello world")).toBeInTheDocument();
  });

  it("should align user messages to the right", () => {
    const { container } = renderWithProviders(
      <MessageBubble role="user" content="Hello" />,
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-end");
  });

  it("should align assistant messages to the left", () => {
    const { container } = renderWithProviders(
      <MessageBubble role="assistant" content="Hi there" />,
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-start");
  });

  it("should display timestamp when provided", () => {
    renderWithProviders(
      <MessageBubble
        role="user"
        content="Hello"
        timestamp="2026-01-15T10:30:00Z"
      />,
    );
    // timestamp is rendered as localeTimeString
    expect(screen.getByText(/\d{1,2}:\d{2}/)).toBeInTheDocument();
  });

  it("should display reliability percent for assistant message", () => {
    renderWithProviders(
      <MessageBubble
        role="assistant"
        content="Hello"
        reliabilityPercent={87}
      />,
    );

    expect(screen.getByText(/fiabilite: 87%/i)).toBeInTheDocument();
  });
});
