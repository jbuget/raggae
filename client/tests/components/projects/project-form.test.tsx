import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectForm } from "@/components/projects/project-form";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("ProjectForm", () => {
  it("should render name, description, and system prompt fields", () => {
    renderWithProviders(<ProjectForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/system prompt/i)).toBeInTheDocument();
  });

  it("should disable submit when name is empty", () => {
    renderWithProviders(<ProjectForm onSubmit={vi.fn()} />);

    const button = screen.getByRole("button", { name: /create project/i });
    expect(button).toBeDisabled();
  });

  it("should enable submit when name is filled", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ProjectForm onSubmit={vi.fn()} />);

    await user.type(screen.getByLabelText(/name/i), "My Project");

    const button = screen.getByRole("button", { name: /create project/i });
    expect(button).toBeEnabled();
  });

  it("should call onSubmit with form data", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<ProjectForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/name/i), "My Project");
    await user.type(screen.getByLabelText(/description/i), "A description");
    await user.click(screen.getByRole("button", { name: /create project/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      name: "My Project",
      description: "A description",
      system_prompt: "",
      chunking_strategy: "auto",
      parent_child_chunking: false,
    });
  });

  it("should pre-fill fields with initialData", () => {
    const initialData = {
      id: "proj-1",
      user_id: "user-1",
      name: "Existing",
      description: "Existing desc",
      system_prompt: "Be helpful",
      is_published: false,
      created_at: "2026-01-01T00:00:00Z",
      chunking_strategy: "auto" as const,
      parent_child_chunking: false,
      reindex_status: "idle",
      reindex_progress: 0,
      reindex_total: 0,
    };

    renderWithProviders(
      <ProjectForm
        initialData={initialData}
        onSubmit={vi.fn()}
        submitLabel="Save"
      />,
    );

    expect(screen.getByLabelText(/name/i)).toHaveValue("Existing");
    expect(screen.getByLabelText(/description/i)).toHaveValue("Existing desc");
    expect(screen.getByLabelText(/system prompt/i)).toHaveValue("Be helpful");
    expect(screen.getByRole("button", { name: /save/i })).toBeInTheDocument();
  });

  it("should show reindex warning when toggling parent-child chunking", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    const initialData = {
      id: "proj-1",
      user_id: "user-1",
      name: "Existing",
      description: "",
      system_prompt: "",
      is_published: false,
      created_at: "2026-01-01T00:00:00Z",
      chunking_strategy: "auto" as const,
      parent_child_chunking: false,
      reindex_status: "idle",
      reindex_progress: 0,
      reindex_total: 0,
    };

    renderWithProviders(
      <ProjectForm
        initialData={initialData}
        onSubmit={onSubmit}
        submitLabel="Save"
      />,
    );

    // Toggle parent-child chunking on
    await user.click(screen.getByLabelText(/enable parent-child chunking/i));
    await user.click(screen.getByRole("button", { name: /save/i }));

    // Warning dialog should appear
    expect(screen.getByText(/reindexation requise/i)).toBeInTheDocument();

    // onSubmit should NOT have been called yet
    expect(onSubmit).not.toHaveBeenCalled();

    // Confirm
    await user.click(screen.getByRole("button", { name: /confirmer/i }));

    // Now onSubmit should have been called
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ parent_child_chunking: true }),
    );
  });

  it("should not show reindex warning when parent-child chunking is unchanged", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    const initialData = {
      id: "proj-1",
      user_id: "user-1",
      name: "Existing",
      description: "",
      system_prompt: "",
      is_published: false,
      created_at: "2026-01-01T00:00:00Z",
      chunking_strategy: "auto" as const,
      parent_child_chunking: false,
      reindex_status: "idle",
      reindex_progress: 0,
      reindex_total: 0,
    };

    renderWithProviders(
      <ProjectForm
        initialData={initialData}
        onSubmit={onSubmit}
        submitLabel="Save"
      />,
    );

    await user.click(screen.getByRole("button", { name: /save/i }));

    // No warning, onSubmit called directly
    expect(onSubmit).toHaveBeenCalled();
  });
});
