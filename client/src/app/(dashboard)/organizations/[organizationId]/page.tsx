import { OrganizationSettings } from "@/components/organizations/organization-settings";

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
