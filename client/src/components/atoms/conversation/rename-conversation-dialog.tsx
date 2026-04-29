"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

interface RenameConversationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialTitle: string;
  onConfirm: (title: string) => void;
}

interface DialogBodyProps {
  initialTitle: string;
  onConfirm: (title: string) => void;
  onOpenChange: (open: boolean) => void;
}

function DialogBody({ initialTitle, onConfirm, onOpenChange }: DialogBodyProps) {
  const [value, setValue] = useState(initialTitle);
  const t = useTranslations("chat.sidebar");
  const tCommon = useTranslations("common");

  function handleConfirm() {
    const trimmed = value.trim();
    if (trimmed) onConfirm(trimmed);
    onOpenChange(false);
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>{t("renameTitle")}</DialogTitle>
        <DialogDescription>{t("renameDescription")}</DialogDescription>
      </DialogHeader>
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={t("renamePlaceholder")}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleConfirm();
        }}
        autoFocus
      />
      <DialogFooter>
        <Button variant="outline" onClick={() => onOpenChange(false)}>
          {tCommon("cancel")}
        </Button>
        <Button onClick={handleConfirm} disabled={!value.trim()}>
          {tCommon("save")}
        </Button>
      </DialogFooter>
    </>
  );
}

export function RenameConversationDialog({
  open,
  onOpenChange,
  initialTitle,
  onConfirm,
}: RenameConversationDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton={false}>
        {open && (
          <DialogBody
            initialTitle={initialTitle}
            onConfirm={onConfirm}
            onOpenChange={onOpenChange}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
