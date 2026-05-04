"use client";

import { useTranslations } from "next-intl";
import { ProjectSnapshotsList } from "@/components/organisms/project/project-snapshots-list";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

interface ProjectSnapshotsSheetProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ProjectSnapshotsSheet({ projectId, open, onOpenChange }: ProjectSnapshotsSheetProps) {
  const t = useTranslations("projects.settings");

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full flex-col sm:max-w-xl">
        <SheetHeader className="border-b pb-4">
          <SheetTitle>{t("tabs.history")}</SheetTitle>
        </SheetHeader>
        <div className="flex-1 overflow-y-auto px-1 py-4">
          <ProjectSnapshotsList projectId={projectId} />
        </div>
      </SheetContent>
    </Sheet>
  );
}
