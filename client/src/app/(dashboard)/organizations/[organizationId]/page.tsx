import { OrganizationSettings } from "@/components/organisms/organization/organization-settings";

type OrganizationSettingsPageProps = {
  params: Promise<{
    organizationId: string;
  }>;
};

export default async function OrganizationSettingsPage({
  params,
}: OrganizationSettingsPageProps) {
  const { organizationId } = await params;
  return <OrganizationSettings organizationId={organizationId} />;
}
