import { supabaseAdmin } from '@/lib/supabaseAdmin';

async function getStats() {
  const [users, activeUsers, pendingReports, pendingPhotos, premiumUsers, conversations] = await Promise.all([
    supabaseAdmin.from('profiles').select('id', { count: 'exact', head: true }),
    supabaseAdmin.from('profiles').select('id', { count: 'exact', head: true }).eq('status', 'active'),
    supabaseAdmin.from('reports').select('id', { count: 'exact', head: true }).eq('status', 'pending'),
    supabaseAdmin.from('photos').select('id', { count: 'exact', head: true }).eq('moderation_status', 'pending'),
    supabaseAdmin.from('profiles').select('id', { count: 'exact', head: true }).eq('is_premium', true),
    supabaseAdmin.from('conversations').select('id', { count: 'exact', head: true }),
  ]);

  return {
    totalUsers: users.count ?? 0,
    activeUsers: activeUsers.count ?? 0,
    pendingReports: pendingReports.count ?? 0,
    pendingPhotos: pendingPhotos.count ?? 0,
    premiumUsers: premiumUsers.count ?? 0,
    conversations: conversations.count ?? 0,
  };
}

function StatCard({ label, value, emoji, alert }: { label: string; value: number; emoji: string; alert?: boolean }) {
  return (
    <div className={`rounded-xl border p-5 ${alert && value > 0 ? 'border-rose-500/50 bg-rose-950/20' : 'border-zinc-800 bg-zinc-900'}`}>
      <div className="text-2xl mb-2">{emoji}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-sm text-zinc-400 mt-1">{label}</div>
    </div>
  );
}

export default async function DashboardPage() {
  const stats = await getStats();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Resumen</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Usuarios totales" value={stats.totalUsers} emoji="👥" />
        <StatCard label="Usuarios activos" value={stats.activeUsers} emoji="✅" />
        <StatCard label="Usuarios Premium" value={stats.premiumUsers} emoji="⭐" />
        <StatCard label="Conversaciones" value={stats.conversations} emoji="💬" />
        <StatCard label="Reportes pendientes" value={stats.pendingReports} emoji="🚩" alert />
        <StatCard label="Fotos por moderar" value={stats.pendingPhotos} emoji="🖼️" alert />
      </div>
    </div>
  );
}
