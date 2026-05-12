import { Header } from "@/components/organisms/layout/header";
import { Sidebar } from "@/components/organisms/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto px-6 pb-6 [scrollbar-gutter:stable]">{children}</main>
      </div>
    </div>
  );
}
