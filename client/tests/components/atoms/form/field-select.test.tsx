import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FieldSelect } from "@/components/atoms/form/field-select";
import { renderWithProviders } from "../../../helpers/render";

describe("FieldSelect", () => {
  it("should render label and select linked by htmlFor", () => {
    renderWithProviders(
      <FieldSelect id="role" label="Role">
        <option value="user">User</option>
      </FieldSelect>,
    );
    expect(screen.getByLabelText("Role")).toBeInTheDocument();
    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  it("should render all options", () => {
    renderWithProviders(
      <FieldSelect id="role" label="Role">
        <option value="owner">Owner</option>
        <option value="maker">Maker</option>
        <option value="user">User</option>
      </FieldSelect>,
    );
    expect(screen.getByRole("option", { name: "Owner" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Maker" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "User" })).toBeInTheDocument();
  });

  it("should render hint when provided", () => {
    renderWithProviders(
      <FieldSelect id="role" label="Role" hint="Choose a role">
        <option value="user">User</option>
      </FieldSelect>,
    );
    expect(screen.getByText("Choose a role")).toBeInTheDocument();
  });

  it("should not render hint when omitted", () => {
    renderWithProviders(
      <FieldSelect id="role" label="Role">
        <option value="user">User</option>
      </FieldSelect>,
    );
    expect(screen.queryByText(/choose/i)).not.toBeInTheDocument();
  });

  it("should forward native select props", () => {
    renderWithProviders(
      <FieldSelect id="role" label="Role" defaultValue="maker">
        <option value="owner">Owner</option>
        <option value="maker">Maker</option>
      </FieldSelect>,
    );
    expect(screen.getByRole("combobox")).toHaveValue("maker");
  });
});
