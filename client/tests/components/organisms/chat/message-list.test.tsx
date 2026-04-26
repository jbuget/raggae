import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MessageList } from "@/components/organisms/chat/message-list";
import { renderWithProviders } from "../../../helpers/render";
import type { MessageResponse } from "@/lib/types/api";

const messages: MessageResponse[] = [
  {
    id: "1",
    conversation_id: "conv-1",
    role: "user",
    content: "Bonjour",
    created_at: "2024-01-15T10:00:00Z",
  },
  {
    id: "2",
    conversation_id: "conv-1",
    role: "assistant",
    content: "Bonjour, comment puis-je vous aider ?",
    created_at: "2024-01-15T10:00:05Z",
  },
];

describe("MessageList", () => {
  it("should render all messages", () => {
    renderWithProviders(
      <MessageList
        messages={messages}
        streamedContent=""
        isStreaming={false}
        isSending={false}
        streamError={null}
        streamedSourceDocuments={[]}
        onSourceClick={vi.fn()}
      />,
    );
    expect(screen.getByText("Bonjour")).toBeInTheDocument();
    expect(screen.getByText("Bonjour, comment puis-je vous aider ?")).toBeInTheDocument();
  });

  it("should render the streaming indicator while sending", () => {
    renderWithProviders(
      <MessageList
        messages={[]}
        streamedContent=""
        isStreaming={false}
        isSending={true}
        streamError={null}
        streamedSourceDocuments={[]}
        onSourceClick={vi.fn()}
      />,
    );
    expect(screen.getByText(/thinking/i)).toBeInTheDocument();
  });

  it("should render streamed content as an assistant bubble", () => {
    renderWithProviders(
      <MessageList
        messages={[]}
        streamedContent="Réponse en cours..."
        isStreaming={true}
        isSending={false}
        streamError={null}
        streamedSourceDocuments={[]}
        onSourceClick={vi.fn()}
      />,
    );
    expect(screen.getByText("Réponse en cours...")).toBeInTheDocument();
  });

  it("should display the stream error when idle", () => {
    renderWithProviders(
      <MessageList
        messages={[]}
        streamedContent=""
        isStreaming={false}
        isSending={false}
        streamError="Erreur réseau"
        streamedSourceDocuments={[]}
        onSourceClick={vi.fn()}
      />,
    );
    expect(screen.getByText("Erreur réseau")).toBeInTheDocument();
  });
});
