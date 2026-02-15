import { createRef } from "react";
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScrollArea } from "@/components/ui/scroll-area";

describe("ScrollArea", () => {
  it("forwards root ref", () => {
    const ref = createRef<HTMLDivElement>();

    render(
      <ScrollArea ref={ref}>
        <div>content</div>
      </ScrollArea>,
    );

    expect(ref.current).toBeInstanceOf(HTMLDivElement);
    expect(ref.current?.dataset.slot).toBe("scroll-area");
  });
});
