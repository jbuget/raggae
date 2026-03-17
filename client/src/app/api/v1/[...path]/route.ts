import { NextRequest, NextResponse } from "next/server";
import { buildResponseHeaders, buildUpstreamHeaders } from "@/lib/proxy/headers";
import { buildUpstreamUrl } from "@/lib/proxy/url";

export const runtime = "nodejs";

type RouteParams = { params: Promise<{ path: string[] }> };

async function handler(request: NextRequest, { params }: RouteParams) {
  const { path } = await params;
  const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

  const url = buildUpstreamUrl(backendUrl, path, request.nextUrl.searchParams);
  const headers = buildUpstreamHeaders(
    request.headers,
    request.headers.get("x-forwarded-for") ?? undefined,
  );

  const hasBody = !["GET", "HEAD"].includes(request.method);

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: request.method,
      headers,
      body: hasBody ? request.body : undefined,
      // @ts-expect-error — duplex requis pour le streaming du body en Node.js
      duplex: hasBody ? "half" : undefined,
    });
  } catch {
    return new NextResponse("Bad Gateway", { status: 502 });
  }

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: buildResponseHeaders(upstream.headers),
  });
}

export {
  handler as GET,
  handler as POST,
  handler as PUT,
  handler as DELETE,
  handler as PATCH,
};
