import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageBubble } from "@/components/chat/message-bubble";
import { renderWithProviders } from "../../helpers/render";

describe("MessageBubble", () => {
  it("renders assistant markdown content", () => {
    renderWithProviders(
      <MessageBubble
        role="assistant"
        content={"## Title\nThis is **bold** and `code`\n- first\n- second"}
      />,
    );

    expect(screen.getByRole("heading", { name: "Title" })).toBeInTheDocument();
    expect(screen.getByText("bold").tagName).toBe("STRONG");
    expect(screen.getByText("code").tagName).toBe("CODE");
    expect(screen.getByText("first")).toBeInTheDocument();
    expect(screen.getByText("second")).toBeInTheDocument();
  });
});
