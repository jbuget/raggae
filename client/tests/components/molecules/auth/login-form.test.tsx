import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { LoginForm } from "@/components/molecules/auth/login-form";
import { renderWithProviders } from "../../../helpers/render";

const mockSignIn = vi.fn();
vi.mock("next-auth/react", async () => {
  const actual = await vi.importActual("next-auth/react");
  return { ...actual, signIn: (...args: unknown[]) => mockSignIn(...args) };
});

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => ({ get: () => null }),
}));

describe("LoginForm", () => {
  afterEach(() => { vi.clearAllMocks(); });

  it("should render email and password inputs", () => {
    renderWithProviders(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("should have a disabled submit button when fields are empty", () => {
    renderWithProviders(<LoginForm />);
    expect(screen.getByRole("button", { name: /sign in/i })).toBeDisabled();
  });

  it("should enable submit button when both fields are filled", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    expect(screen.getByRole("button", { name: /sign in/i })).toBeEnabled();
  });

  it("should call signIn and redirect to /projects on success", async () => {
    mockSignIn.mockResolvedValue({ error: null });
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(mockSignIn).toHaveBeenCalledWith("credentials", {
      email: "test@example.com",
      password: "password123",
      redirect: false,
    });
    expect(mockPush).toHaveBeenCalledWith("/projects");
  });

  it("should display an error alert on failed sign in", async () => {
    mockSignIn.mockResolvedValue({ error: "CredentialsSignin" });
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "wrong");
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid email or password");
  });

  it("should render the Microsoft SSO button when entraEnabled is true", () => {
    renderWithProviders(<LoginForm entraEnabled />);
    expect(screen.getByRole("button", { name: /microsoft/i })).toBeInTheDocument();
  });

  it("should not render the Microsoft SSO button when entraEnabled is false", () => {
    renderWithProviders(<LoginForm />);
    expect(screen.queryByRole("button", { name: /microsoft/i })).not.toBeInTheDocument();
  });
});
