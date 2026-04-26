import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageTemplate } from "@/components/templates/page-template";
import { renderWithProviders } from "../../helpers/render";

describe("PageTemplate", () => {
  it("should render the title as an h1", () => {
    renderWithProviders(
      <PageTemplate title="My Page">
        <p>content</p>
      </PageTemplate>,
    );
    expect(screen.getByRole("heading", { level: 1, name: "My Page" })).toBeInTheDocument();
  });

  it("should render the description when provided", () => {
    renderWithProviders(
      <PageTemplate title="My Page" description="A short description">
        <p>content</p>
      </PageTemplate>,
    );
    expect(screen.getByText("A short description")).toBeInTheDocument();
  });

  it("should not render a description element when omitted", () => {
    renderWithProviders(
      <PageTemplate title="My Page">
        <span>content</span>
      </PageTemplate>,
    );
    expect(screen.queryByRole("paragraph")).not.toBeInTheDocument();
  });

  it("should render the actions slot", () => {
    renderWithProviders(
      <PageTemplate title="My Page" actions={<button>New</button>}>
        <p>content</p>
      </PageTemplate>,
    );
    expect(screen.getByRole("button", { name: "New" })).toBeInTheDocument();
  });

  it("should render children", () => {
    renderWithProviders(
      <PageTemplate title="My Page">
        <p>Hello world</p>
      </PageTemplate>,
    );
    expect(screen.getByText("Hello world")).toBeInTheDocument();
  });
});
