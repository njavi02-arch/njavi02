import Link from 'next/link';
import { requireAdmin } from '@/lib/requireAdmin';
import { logoutAction } from '../login/actions';

const NAV = [
  { href: '/dashboard', label: 'Resumen', emoji: '📊' },
  { href: '/users', label: 'Usuarios', emoji: '👥' },
  { href: '/reports', label: 'Reportes', emoji: '🚩' },
  { href: '/photos', label: 'Moderación de fotos', emoji: '🖼️' },
  { href: '/config', label: 'Configuración', emoji: '⚙️' },
];

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const admin = await requireAdmin();

  return (
    <div className="min-h-screen flex bg-zinc-950 text-zinc-100">
      <aside className="w-64 shrink-0 border-r border-zinc-800 p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-8 px-2">
          <span className="text-2xl">🪐</span>
          <span className="font-bold text-lg">Orbita Admin</span>
        </div>
        <nav className="flex flex-col gap-1 flex-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-300 hover:bg-zinc-900 hover:text-white transition-colors"
            >
              <span>{item.emoji}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-zinc-800 pt-4 mt-4">
          <p className="text-xs text-zinc-500 px-2 mb-2">
            {admin.email ?? admin.id} · {admin.role}
          </p>
          <form action={logoutAction}>
            <button type="submit" className="w-full text-left text-sm text-zinc-400 hover:text-white px-2 py-1.5">
              Cerrar sesión
            </button>
          </form>
        </div>
      </aside>
      <main className="flex-1 p-8 overflow-y-auto">{children}</main>
    </div>
  );
}
