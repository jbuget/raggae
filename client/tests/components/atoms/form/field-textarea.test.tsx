import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FieldTextarea } from "@/components/atoms/form/field-textarea";
import { renderWithProviders } from "../../../helpers/render";

describe("FieldTextarea", () => {
  it("should render label and textarea linked by htmlFor", () => {
    renderWithProviders(<FieldTextarea id="bio" label="Biography" />);
    expect(screen.getByLabelText("Biography")).toBeInTheDocument();
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });

  it("should render hint when provided", () => {
    renderWithProviders(<FieldTextarea id="bio" label="Biography" hint="Describe yourself" />);
    expect(screen.getByText("Describe yourself")).toBeInTheDocument();
  });

  it("should not render hint when omitted", () => {
    renderWithProviders(<FieldTextarea id="bio" label="Biography" />);
    expect(screen.queryByText(/describe/i)).not.toBeInTheDocument();
  });

  it("should render labelExtra alongside the label", () => {
    renderWithProviders(
      <FieldTextarea id="bio" label="Biography" labelExtra={<span>optional</span>} />,
    );
    expect(screen.getByText("optional")).toBeInTheDocument();
  });

  it("should forward native textarea props", () => {
    renderWithProviders(
      <FieldTextarea id="bio" label="Biography" placeholder="Tell us about you" rows={5} />,
    );
    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveAttribute("placeholder", "Tell us about you");
    expect(textarea).toHaveAttribute("rows", "5");
  });
});
