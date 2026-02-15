import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { MessageInput } from "@/components/chat/message-input";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("MessageInput", () => {
  it("should render textarea and send button", () => {
    renderWithProviders(<MessageInput onSend={vi.fn()} />);

    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });

  it("should disable send button when empty", () => {
    renderWithProviders(<MessageInput onSend={vi.fn()} />);

    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("should call onSend when button is clicked", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<MessageInput onSend={onSend} />);

    await user.type(screen.getByLabelText(/message/i), "Hello");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith("Hello");
  });

  it("should send on Enter key", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<MessageInput onSend={onSend} />);

    const textarea = screen.getByLabelText(/message/i);
    await user.type(textarea, "Hello{Enter}");

    expect(onSend).toHaveBeenCalledWith("Hello");
  });

  it("should not send on Shift+Enter", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<MessageInput onSend={onSend} />);

    const textarea = screen.getByLabelText(/message/i);
    await user.type(textarea, "Hello{Shift>}{Enter}{/Shift}");

    expect(onSend).not.toHaveBeenCalled();
  });

  it("should clear input after sending", async () => {
    const user = userEvent.setup();
    renderWithProviders(<MessageInput onSend={vi.fn()} />);

    const textarea = screen.getByLabelText(/message/i);
    await user.type(textarea, "Hello");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(textarea).toHaveValue("");
  });

  it("should disable when disabled prop is true", () => {
    renderWithProviders(<MessageInput onSend={vi.fn()} disabled />);

    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });
});
