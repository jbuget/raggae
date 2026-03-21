import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

// Intercept next-auth internal endpoints to prevent unhandled fetch errors in tests
export const server = setupServer(
  http.get("http://localhost:3000/api/auth/session", () =>
    HttpResponse.json({ user: null, expires: "" }),
  ),
  http.post("http://localhost:3000/api/auth/_log", () =>
    HttpResponse.json({}),
  ),
);
