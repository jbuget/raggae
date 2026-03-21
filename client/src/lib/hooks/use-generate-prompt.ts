"use client";

import { useMutation } from "@tanstack/react-query";
import { generateProjectPrompt } from "@/lib/api/projects";
import type { GeneratePromptRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useGeneratePrompt() {
  const { token } = useAuth();

  return useMutation({
    mutationFn: (data: GeneratePromptRequest) =>
      generateProjectPrompt(token!, data),
  });
}
