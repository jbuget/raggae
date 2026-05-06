const fs = require('fs');
const file = 'client/src/components/organisms/project/settings/project-advanced-panel.tsx';
let d = fs.readFileSync(file, 'utf8');
d = d.replace(/const orgHasAnyDefaults = [^;]+;/, `const orgHasAnyDefaults = orgHasModels || orgHasIndexing || orgHasRetrieval || orgHasReranking || orgHasChatHistory;
  const userHasAnyDefaults = userHasModels || userHasIndexing || userHasRetrieval || userHasReranking || userHasChatHistory;`);
d = d.replace(/const anySectionOverrides =[^;]+;\n/s, `const anySectionOverrides =
    (orgHasModels && project.overrides_models_from_org) ||
    (orgHasIndexing && project.overrides_indexing_from_org) ||
    (orgHasRetrieval && project.overrides_retrieval_from_org) ||
    (orgHasReranking && project.overrides_reranking_from_org) ||
    (orgHasChatHistory && project.overrides_chat_history_from_org);
  const anyUserSectionOverrides =
    (userHasModels && project.overrides_models_from_user) ||
    (userHasIndexing && project.overrides_indexing_from_user) ||
    (userHasRetrieval && project.overrides_retrieval_from_user) ||
    (userHasReranking && project.overrides_reranking_from_user) ||
    (userHasChatHistory && project.overrides_chat_history_from_user);
`);
d = d.replace(/const globalOverride = forceGlobalEnabled \|\| anySectionOverrides;/, `const globalOverride = forceGlobalEnabled || anySectionOverrides;
  const globalUserOverride = forceGlobalEnabled || anyUserSectionOverrides;`);
d = d.replace(/function handleGlobalToggle\(\) \{[\s\S]*?function handleToggleOverride/m, `function handleGlobalToggle() {
    if (globalOverride) {
      setForceGlobalEnabled(false);
      updateProject.mutate(
        {
          ...(orgHasModels && { overrides_models_from_org: false }),
          ...(orgHasIndexing && { overrides_indexing_from_org: false }),
          ...(orgHasRetrieval && { overrides_retrieval_from_org: false }),
          ...(orgHasReranking && { overrides_reranking_from_org: false }),
          ...(orgHasChatHistory && { overrides_chat_history_from_org: false }),
        },
        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
      );
    } else {
      setForceGlobalEnabled(true);
    }
  }
  function handleGlobalUserToggle() {
    if (globalUserOverride) {
      setForceGlobalEnabled(false);
      updateProject.mutate(
        {
          ...(userHasModels && { overrides_models_from_user: false }),
          ...(userHasIndexing && { overrides_indexing_from_user: false }),
          ...(userHasRetrieval && { overrides_retrieval_from_user: false }),
          ...(userHasReranking && { overrides_reranking_from_user: false }),
          ...(userHasChatHistory && { overrides_chat_history_from_user: false }),
        },
        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
      );
    } else {
      setForceGlobalEnabled(true);
    }
  }
  function handleToggleOverride`);
d = d.replace(/\{\/\* Global override \*\/\}\n\s*\{orgHasAnyDefaults && \(/, `{/* Global override */}
        {inOrg && orgHasAnyDefaults && (`);
d = d.replace(/<\/div>\n\s*\)\}\n\n\s*<Accordion type="multiple"/, `</div>
        )}
        {!inOrg && userHasAnyDefaults && (
          <div className="flex items-center justify-between gap-4 border-b py-4">
            <div className="space-y-0.5">
              <p className="text-sm font-medium">{t("overrideUserDefaults")}</p>
              <p className="text-xs text-muted-foreground">{t("globalOverrideDescription")}</p>
            </div>
            <Switch
              checked={globalUserOverride}
              onCheckedChange={handleGlobalUserToggle}
              disabled={updateProject.isPending}
            />
          </div>
        )}
        <Accordion type="multiple"`);
// For the sub switches
const locks = ["Models", "Indexing", "Retrieval", "Reranking", "ChatHistory"];
locks.forEach(lock => {
  const switchTarget = new RegExp(`<Switch\\s+id="overrides-${lock.toLowerCase().replace("chathistory", "chat-history")}-user"\\s+checked=\\{project\\.overrides_${lock.toLowerCase().replace("chathistory", "chat_history")}_from_user\\}\\s+onCheckedChange=\\{[^}]+\\}\\s+disabled=\\{updateProject\\.isPending\\}\\s+\\/>`);
  d = d.replace(switchTarget, `<Switch
                      id="overrides-${lock.toLowerCase().replace("chathistory", "chat-history")}-user"
                      checked={project.overrides_${lock.toLowerCase().replace("chathistory", "chat_history")}_from_user}
                      onCheckedChange={() => handleToggleOverride("overrides_${lock.toLowerCase().replace("chathistory", "chat_history")}_from_user", project.overrides_${lock.toLowerCase().replace("chathistory", "chat_history")}_from_user)}
                      disabled={(!inOrg && !globalUserOverride) || updateProject.isPending}
                    />`);
});
fs.writeFileSync(file, d);
