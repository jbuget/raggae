"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useCurrentUserProfile, useUpdateUserFullName } from "@/lib/hooks/use-user-profile";

export function UserProfilePanel() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const { data: userProfile, isLoading } = useCurrentUserProfile();
  const updateUserFullName = useUpdateUserFullName();
  const [fullName, setFullName] = useState("");

  const effectiveFullName = fullName || userProfile?.full_name || "";

  return (
    <Card className="space-y-4 p-5">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{t("profile.title")}</h2>
        <p className="text-sm text-muted-foreground">{t("profile.description")}</p>
      </div>
      {isLoading ? (
        <Skeleton className="h-10 w-full" />
      ) : (
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user-email">{t("profile.emailLabel")}</Label>
            <Input id="user-email" value={userProfile?.email ?? ""} disabled />
          </div>
          <div className="space-y-2">
            <Label htmlFor="user-full-name">{t("profile.fullNameLabel")}</Label>
            <Input
              id="user-full-name"
              value={effectiveFullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder={t("profile.fullNamePlaceholder")}
            />
          </div>
          <Button
            type="button"
            onClick={() =>
              updateUserFullName.mutate(effectiveFullName.trim(), {
                onSuccess: () => {
                  toast.success(t("profile.saveSuccess"));
                  setFullName("");
                },
                onError: (error) =>
                  toast.error((error as Error).message || t("profile.saveError")),
              })
            }
            disabled={!effectiveFullName.trim() || updateUserFullName.isPending}
          >
            {updateUserFullName.isPending ? tCommon("saving") : t("profile.save")}
          </Button>
        </div>
      )}
    </Card>
  );
}
