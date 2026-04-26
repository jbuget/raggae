import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { MessageBubble } from "@/components/molecules/chat/message-bubble";
import { renderWithProviders } from "../../../helpers/render";

describe("MessageBubble", () => {
  it("should render a user message as plain text", () => {
    renderWithProviders(<MessageBubble role="user" content="Hello!" />);
    expect(screen.getByText("Hello!")).toBeInTheDocument();
  });

  it("should render assistant markdown as HTML", () => {
    renderWithProviders(
      <MessageBubble
        role="assistant"
        content={"## Title\nThis is **bold** and `code`\n- first\n- second"}
      />,
    );
    expect(screen.getByRole("heading", { name: "Title" })).toBeInTheDocument();
    expect(screen.getByText("bold").tagName).toBe("STRONG");
    expect(screen.getByText("code").tagName).toBe("CODE");
  });

  it("should display source badges for assistant messages", () => {
    renderWithProviders(
      <MessageBubble
        role="assistant"
        content="Answer"
        sourceDocuments={[
          { documentId: "doc-a", documentName: "doc-a.md", chunkIds: ["c1"] },
          { documentId: "doc-b", documentName: "doc-b.pdf", chunkIds: ["c2"] },
        ]}
      />,
    );
    expect(screen.getByText("doc-a.md")).toBeInTheDocument();
    expect(screen.getByText("doc-b.pdf")).toBeInTheDocument();
  });

  it("should not display source badges for user messages", () => {
    renderWithProviders(
      <MessageBubble
        role="user"
        content="Hello"
        sourceDocuments={[
          { documentId: "doc-a", documentName: "doc-a.md", chunkIds: ["c1"] },
        ]}
      />,
    );
    expect(screen.queryByText("doc-a.md")).not.toBeInTheDocument();
  });

  it("should call onSourceClick when a source badge is clicked", async () => {
    const onSourceClick = vi.fn();
    const user = userEvent.setup();
    const source = { documentId: "doc-a", documentName: "doc-a.md", chunkIds: ["c1"] };
    renderWithProviders(
      <MessageBubble
        role="assistant"
        content="Answer"
        sourceDocuments={[source]}
        onSourceClick={onSourceClick}
      />,
    );
    await user.click(screen.getByText("doc-a.md"));
    expect(onSourceClick).toHaveBeenCalledWith(source);
  });

  it("should display the timestamp when provided", () => {
    renderWithProviders(
      <MessageBubble role="user" content="Hi" timestamp="2024-01-15T10:30:00Z" />,
    );
    const formatted = new Date("2024-01-15T10:30:00Z").toLocaleTimeString();
    expect(screen.getByText(formatted)).toBeInTheDocument();
  });
});
