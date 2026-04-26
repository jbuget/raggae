import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { LocaleSelector } from "@/components/molecules/layout/locale-selector";
import { renderWithProviders } from "../../../helpers/render";

const mutateMock = vi.fn();

vi.mock("@/lib/hooks/use-user-profile", () => ({
  useUpdateUserLocale: () => ({ mutate: mutateMock }),
}));

vi.mock("next-intl", async (importOriginal) => {
  const actual = await importOriginal<typeof import("next-intl")>();
  return { ...actual, useLocale: () => "en" };
});

describe("LocaleSelector", () => {
  it("should render a trigger button", () => {
    renderWithProviders(<LocaleSelector />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should display the current locale flag", () => {
    renderWithProviders(<LocaleSelector />);
    expect(screen.getByText("🇬🇧")).toBeInTheDocument();
  });

  it("should open the dropdown and list available locales on click", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LocaleSelector />);
    await user.click(screen.getByRole("button"));
    expect(screen.getByText(/english/i)).toBeInTheDocument();
    expect(screen.getByText(/français/i)).toBeInTheDocument();
  });

  it("should call mutate when a different locale is selected", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LocaleSelector />);
    await user.click(screen.getByRole("button"));
    await user.click(screen.getByText(/français/i));
    expect(mutateMock).toHaveBeenCalledWith(
      { locale: "fr" },
      expect.any(Object),
    );
  });
});
