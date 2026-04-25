import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FieldInput } from "@/components/atoms/form/field-input";
import { renderWithProviders } from "../../../helpers/render";

describe("FieldInput", () => {
  it("should render label and input linked by htmlFor", () => {
    renderWithProviders(<FieldInput id="name" label="Full name" />);
    expect(screen.getByLabelText("Full name")).toBeInTheDocument();
  });

  it("should render hint when provided", () => {
    renderWithProviders(<FieldInput id="name" label="Full name" hint="Max 255 characters" />);
    expect(screen.getByText("Max 255 characters")).toBeInTheDocument();
  });

  it("should not render hint when omitted", () => {
    renderWithProviders(<FieldInput id="name" label="Full name" />);
    expect(screen.queryByRole("paragraph")).not.toBeInTheDocument();
  });

  it("should render labelExtra alongside the label", () => {
    renderWithProviders(
      <FieldInput id="name" label="Full name" labelExtra={<span>optional</span>} />,
    );
    expect(screen.getByText("optional")).toBeInTheDocument();
  });

  it("should forward native input props", () => {
    renderWithProviders(
      <FieldInput id="email" label="Email" type="email" placeholder="you@example.com" />,
    );
    const input = screen.getByLabelText("Email");
    expect(input).toHaveAttribute("type", "email");
    expect(input).toHaveAttribute("placeholder", "you@example.com");
  });
});
