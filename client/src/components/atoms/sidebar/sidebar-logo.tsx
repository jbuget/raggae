import Link from "next/link";

export function SidebarLogo() {
  return (
    <div className="flex h-14 items-center border-b px-6">
      <Link href="/projects" className="text-xl font-bold">
        Raggae
      </Link>
    </div>
  );
}
