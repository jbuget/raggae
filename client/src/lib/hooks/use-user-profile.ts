"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentUser, updateUserFullName, updateUserLocale } from "@/lib/api/auth";
import type { UpdateUserLocaleRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useCurrentUserProfile() {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["current-user-profile"],
    queryFn: () => getCurrentUser(token!),
    enabled: !!token,
  });
}

export function useUpdateUserFullName() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (fullName: string) => updateUserFullName(token!, { full_name: fullName }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["current-user-profile"] });
    },
  });
}

export function useUpdateUserLocale() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UpdateUserLocaleRequest) => updateUserLocale(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["current-user-profile"] });
    },
  });
}
