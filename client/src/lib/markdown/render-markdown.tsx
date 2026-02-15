import type { ReactNode } from "react";

function parseInline(text: string): ReactNode[] {
  const result: ReactNode[] = [];
  const pattern = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null = pattern.exec(text);
  let key = 0;

  while (match) {
    const [token] = match;
    if (match.index > lastIndex) {
      result.push(text.slice(lastIndex, match.index));
    }

    if (token.startsWith("**")) {
      result.push(<strong key={`strong-${key++}`}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("*")) {
      result.push(<em key={`em-${key++}`}>{token.slice(1, -1)}</em>);
    } else if (token.startsWith("`")) {
      result.push(
        <code
          key={`code-${key++}`}
          className="rounded bg-black/10 px-1 py-0.5 font-mono text-xs"
        >
          {token.slice(1, -1)}
        </code>,
      );
    }

    lastIndex = pattern.lastIndex;
    match = pattern.exec(text);
  }

  if (lastIndex < text.length) {
    result.push(text.slice(lastIndex));
  }

  return result;
}

export function renderMarkdown(markdown: string): ReactNode {
  const lines = markdown.split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i += 1;
      continue;
    }

    if (line.startsWith("```")) {
      const codeLines: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i += 1;
      }
      i += 1;
      blocks.push(
        <pre
          key={`pre-${i}`}
          className="overflow-x-auto rounded-md bg-black/10 p-2 font-mono text-xs"
        >
          <code>{codeLines.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    const heading = /^(#{1,6})\s+(.+)$/.exec(line);
    if (heading) {
      const level = Math.min(heading[1].length, 6);
      const content = parseInline(heading[2]);
      if (level === 1) {
        blocks.push(
          <h1 key={`h-${i}`} className="font-semibold">
            {content}
          </h1>,
        );
      } else if (level === 2) {
        blocks.push(
          <h2 key={`h-${i}`} className="font-semibold">
            {content}
          </h2>,
        );
      } else if (level === 3) {
        blocks.push(
          <h3 key={`h-${i}`} className="font-semibold">
            {content}
          </h3>,
        );
      } else if (level === 4) {
        blocks.push(
          <h4 key={`h-${i}`} className="font-semibold">
            {content}
          </h4>,
        );
      } else if (level === 5) {
        blocks.push(
          <h5 key={`h-${i}`} className="font-semibold">
            {content}
          </h5>,
        );
      } else {
        blocks.push(
          <h6 key={`h-${i}`} className="font-semibold">
            {content}
          </h6>,
        );
      }
      i += 1;
      continue;
    }

    const unorderedItems: string[] = [];
    while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
      unorderedItems.push(lines[i].replace(/^[-*]\s+/, ""));
      i += 1;
    }
    if (unorderedItems.length) {
      blocks.push(
        <ul key={`ul-${i}`} className="list-disc space-y-1 pl-5">
          {unorderedItems.map((item, index) => (
            <li key={`li-${index}`}>{parseInline(item)}</li>
          ))}
        </ul>,
      );
      continue;
    }

    const orderedItems: string[] = [];
    while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
      orderedItems.push(lines[i].replace(/^\d+\.\s+/, ""));
      i += 1;
    }
    if (orderedItems.length) {
      blocks.push(
        <ol key={`ol-${i}`} className="list-decimal space-y-1 pl-5">
          {orderedItems.map((item, index) => (
            <li key={`li-${index}`}>{parseInline(item)}</li>
          ))}
        </ol>,
      );
      continue;
    }

    blocks.push(
      <p key={`p-${i}`} className="whitespace-pre-wrap">
        {parseInline(line)}
      </p>,
    );
    i += 1;
  }

  return <div className="space-y-2 text-sm">{blocks}</div>;
}
