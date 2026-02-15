import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChatPanel } from "@/components/chat/chat-panel";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useMessages: () => ({
    data: [
      {
        id: "msg-user",
        conversation_id: "conv-1",
        role: "user",
        content: "Hello",
        created_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "msg-assistant",
        conversation_id: "conv-1",
        role: "assistant",
        content: "Hi there",
        created_at: "2026-01-01T00:00:01Z",
      },
    ],
  }),
  useSendMessage: () => ({
    send: vi.fn(),
    state: "idle",
    streamedContent: "",
    chunks: [
      {
        chunk_id: "chunk-1",
        document_id: "doc-1",
        document_file_name: "atelier-migration-24-11-2025.md",
        content: "chunk content",
        score: 0.91,
      },
      {
        chunk_id: "chunk-2",
        document_id: "doc-1",
        document_file_name: "atelier-migration-24-11-2025.md",
        content: "another chunk",
        score: 0.89,
      },
    ],
  }),
}));

describe("ChatPanel", () => {
  it("should display unique document source name for assistant response", () => {
    renderWithProviders(
      <ChatPanel projectId="proj-1" conversationId="conv-1" />,
    );

    expect(
      screen.getByText(/sources: atelier-migration-24-11-2025.md/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /show sources \(1\)/i }),
    ).toBeInTheDocument();
  });
});
