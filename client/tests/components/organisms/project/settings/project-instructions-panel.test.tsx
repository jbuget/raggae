import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectInstructionsPanel } from "@/components/organisms/project/settings/project-instructions-panel";
import { renderWithProviders } from "../../../../helpers/render";
import { server } from "../../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const mockProject = {
  id: "proj-1",
  user_id: "user-1",
  name: "Test Project",
  description: "A test project",
  system_prompt: "You are a helpful assistant.",
  is_published: false,
  created_at: "2026-01-01T00:00:00Z",
};

describe("ProjectInstructionsPanel", () => {
  it("should render the system prompt textarea", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
    );
    renderWithProviders(<ProjectInstructionsPanel projectId="proj-1" />);
    const textarea = await screen.findByRole("textbox");
    expect(textarea).toHaveValue("You are a helpful assistant.");
  });

  it("should show character count", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
    );
    renderWithProviders(<ProjectInstructionsPanel projectId="proj-1" />);
    expect(await screen.findByText(/\/8000/)).toBeInTheDocument();
  });

  it("should enable save button when content changes", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
    );
    renderWithProviders(<ProjectInstructionsPanel projectId="proj-1" />);
    const textarea = await screen.findByRole("textbox");
    await userEvent.clear(textarea);
    await userEvent.type(textarea, "New prompt");
    const saveButton = screen.getByRole("button");
    expect(saveButton).not.toBeDisabled();
  });

  it("should disable save button when there are no changes", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
    );
    renderWithProviders(<ProjectInstructionsPanel projectId="proj-1" />);
    await screen.findByRole("textbox");
    const saveButton = screen.getByRole("button");
    expect(saveButton).toBeDisabled();
  });
});
