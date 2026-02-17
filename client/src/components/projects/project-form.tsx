"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { ProjectResponse } from "@/lib/types/api";

interface ProjectFormProps {
  initialData?: ProjectResponse;
  onSubmit: (data: { name: string; description: string; system_prompt: string }) => void;
  isLoading?: boolean;
  submitLabel?: string;
}

export function ProjectForm({
  initialData,
  onSubmit,
  isLoading = false,
  submitLabel = "Create Project",
}: ProjectFormProps) {
  const [name, setName] = useState(initialData?.name ?? "");
  const [description, setDescription] = useState(initialData?.description ?? "");
  const [systemPrompt, setSystemPrompt] = useState(initialData?.system_prompt ?? "");

  const isDisabled = !name.trim() || isLoading;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({ name: name.trim(), description, system_prompt: systemPrompt });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {initialData ? "Edit Project" : "New Project"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My project"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What is this project about?"
              rows={3}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="systemPrompt">System Prompt</Label>
            <Textarea
              id="systemPrompt"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Instructions for the AI assistant..."
              rows={5}
            />
          </div>
          <Button type="submit" className="cursor-pointer" disabled={isDisabled}>
            {isLoading ? "Saving..." : submitLabel}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
