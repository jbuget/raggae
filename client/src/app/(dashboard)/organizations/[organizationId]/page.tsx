import { OrganizationSettingsTemplate } from "@/components/templates/organization/organization-settings-template";

type OrganizationSettingsPageProps = {
  params: Promise<{
    organizationId: string;
  }>;
};

export default async function OrganizationSettingsPage({
  params,
}: OrganizationSettingsPageProps) {
  const { organizationId } = await params;
  return <OrganizationSettingsTemplate organizationId={organizationId} />;
}
