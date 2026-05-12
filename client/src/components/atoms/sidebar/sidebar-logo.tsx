import Link from "next/link";

export function SidebarLogo() {
  return (
    <>
      <div className="flex h-14 items-center px-6">
        <Link href="/projects" className="text-xl font-bold">
          Raggae
        </Link>
      </div>
      <div className="mx-3 border-b" />
    </>
  );
}
