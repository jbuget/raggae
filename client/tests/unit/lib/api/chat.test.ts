import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  deleteConversation,
  listConversations,
  listMessages,
  sendMessage,
} from "@/lib/api/chat";
import { server } from "../../../helpers/msw-server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("sendMessage", () => {
  it("should send a message and return response", async () => {
    server.use(
      http.post("/api/v1/projects/proj-1/chat/messages", () => {
        return HttpResponse.json({
          project_id: "proj-1",
          conversation_id: "conv-1",
          message: "Hello",
          answer: "Hi there!",
          chunks: [],
        });
      }),
    );

    const result = await sendMessage("token", "proj-1", {
      message: "Hello",
    });
    expect(result.answer).toBe("Hi there!");
    expect(result.conversation_id).toBe("conv-1");
  });
});

describe("listConversations", () => {
  it("should return conversations", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/chat/conversations", () => {
        return HttpResponse.json([
          {
            id: "conv-1",
            project_id: "proj-1",
            user_id: "user-1",
            created_at: "2026-01-01T00:00:00Z",
            title: "Test conversation",
          },
        ]);
      }),
    );

    const result = await listConversations("token", "proj-1");
    expect(result).toHaveLength(1);
    expect(result[0].title).toBe("Test conversation");
  });
});

describe("deleteConversation", () => {
  it("should delete a conversation", async () => {
    server.use(
      http.delete(
        "/api/v1/projects/proj-1/chat/conversations/conv-1",
        () => {
          return new HttpResponse(null, { status: 204 });
        },
      ),
    );

    const result = await deleteConversation("token", "proj-1", "conv-1");
    expect(result).toBeUndefined();
  });
});

describe("listMessages", () => {
  it("should return messages for a conversation", async () => {
    server.use(
      http.get(
        "/api/v1/projects/proj-1/chat/conversations/conv-1/messages",
        () => {
          return HttpResponse.json([
            {
              id: "msg-1",
              conversation_id: "conv-1",
              role: "user",
              content: "Hello",
              created_at: "2026-01-01T00:00:00Z",
            },
            {
              id: "msg-2",
              conversation_id: "conv-1",
              role: "assistant",
              content: "Hi!",
              created_at: "2026-01-01T00:00:01Z",
            },
          ]);
        },
      ),
    );

    const result = await listMessages("token", "proj-1", "conv-1");
    expect(result).toHaveLength(2);
    expect(result[0].role).toBe("user");
    expect(result[1].role).toBe("assistant");
  });
});
