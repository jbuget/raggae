"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { UserApiKeysPanel } from "@/components/organisms/settings/user-api-keys-panel";
import { UserLocalePanel } from "@/components/organisms/settings/user-locale-panel";
import { UserProfilePanel } from "@/components/organisms/settings/user-profile-panel";
import { UserProjectDefaultsPanel } from "@/components/organisms/settings/user-project-defaults-panel";

const USER_SETTINGS_TABS = ["General", "API Keys", "Projects"] as const;
type UserSettingsTab = (typeof USER_SETTINGS_TABS)[number];

export function UserSettings() {
  const t = useTranslations("settings");
  const router = useRouter();
  const searchParams = useSearchParams();

  const tabFromUrl = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState<UserSettingsTab>(
    USER_SETTINGS_TABS.find((tab) => tab === tabFromUrl) ?? "General",
  );

  const tabLabels: Record<UserSettingsTab, string> = {
    General: t("tabGeneral"),
    "API Keys": t("tabApiKeys"),
    Projects: t("tabProjects"),
  };

  function handleTabChange(tab: UserSettingsTab) {
    setActiveTab(tab);
    const next = new URLSearchParams(searchParams.toString());
    next.set("tab", tab);
    router.replace(`?${next.toString()}`, { scroll: false });
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex flex-wrap items-end gap-4 border-b">
        {USER_SETTINGS_TABS.map((tab) => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              type="button"
              role="tab"
              aria-selected={isActive}
              className={[
                "cursor-pointer border-b-2 px-1 py-3 text-sm whitespace-nowrap transition-colors",
                isActive
                  ? "border-primary text-foreground font-medium"
                  : "border-transparent text-muted-foreground hover:text-foreground",
              ].join(" ")}
              onClick={() => handleTabChange(tab)}
            >
              {tabLabels[tab]}
            </button>
          );
        })}
      </div>

      {activeTab === "General" && (
        <div className="space-y-6">
          <UserProfilePanel />
          <UserLocalePanel />
        </div>
      )}

      {activeTab === "API Keys" && <UserApiKeysPanel />}

      {activeTab === "Projects" && <UserProjectDefaultsPanel />}
    </div>
  );
}
