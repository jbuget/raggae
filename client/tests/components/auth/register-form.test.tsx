import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { RegisterForm } from "@/components/auth/register-form";
import { renderWithProviders } from "../../helpers/render";
import { server } from "../../helpers/msw-server";

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  vi.clearAllMocks();
});
afterAll(() => server.close());

describe("RegisterForm", () => {
  it("should render all input fields", () => {
    renderWithProviders(<RegisterForm />);

    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("should have disabled submit when fields are empty", () => {
    renderWithProviders(<RegisterForm />);

    const button = screen.getByRole("button", { name: /create account/i });
    expect(button).toBeDisabled();
  });

  it("should keep submit disabled when password is too short", async () => {
    const user = userEvent.setup();
    renderWithProviders(<RegisterForm />);

    await user.type(screen.getByLabelText(/full name/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "short");

    const button = screen.getByRole("button", { name: /create account/i });
    expect(button).toBeDisabled();
  });

  it("should register and redirect to login on success", async () => {
    server.use(
      http.post("/api/v1/auth/register", () => {
        return HttpResponse.json(
          {
            id: "user-1",
            email: "test@example.com",
            full_name: "Test User",
            is_active: true,
            created_at: "2026-01-01T00:00:00Z",
          },
          { status: 201 },
        );
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<RegisterForm />);

    await user.type(screen.getByLabelText(/full name/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("should show error on 409 conflict", async () => {
    server.use(
      http.post("/api/v1/auth/register", () => {
        return HttpResponse.json(
          { detail: "Email already registered" },
          { status: 409 },
        );
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<RegisterForm />);

    await user.type(screen.getByLabelText(/full name/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "An account with this email already exists",
    );
  });
});
