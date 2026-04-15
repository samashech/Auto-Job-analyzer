import { Sidebar } from "@/components/dashboard/sidebar";
import { MobileNav } from "@/components/dashboard/mobile-nav";

export default function DashboardGroupLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,rgba(8,145,178,0.2),transparent_45%),linear-gradient(180deg,#020617_0%,#0b1120_100%)]">
      <Sidebar />
      <MobileNav />
      <main className="min-h-screen px-4 py-6 sm:px-6 lg:ml-72 lg:px-10">{children}</main>
    </div>
  );
}
