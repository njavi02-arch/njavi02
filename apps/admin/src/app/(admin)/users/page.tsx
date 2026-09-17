import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { setUserStatus } from './actions';

const STATUS_STYLES: Record<string, string> = {
  active: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  under_review: 'bg-amber-950 text-amber-400 border-amber-800',
  suspended: 'bg-rose-950 text-rose-400 border-rose-800',
  deleted: 'bg-zinc-800 text-zinc-500 border-zinc-700',
};

export default async function UsersPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;

  let query = supabaseAdmin
    .from('profiles')
    .select('id, display_name, status, is_premium, created_at, last_active_at, city')
    .order('created_at', { ascending: false })
    .limit(50);

  if (q) {
    query = query.ilike('display_name', `%${q}%`);
  }

  const { data: users, error } = await query;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Usuarios</h1>

      <form className="mb-4">
        <input
          name="q"
          defaultValue={q ?? ''}
          placeholder="Buscar por nombre…"
          className="w-full max-w-sm rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2 text-sm outline-none focus:border-rose-400"
        />
      </form>

      {error ? <p className="text-rose-400">{error.message}</p> : null}

      <div className="rounded-xl border border-zinc-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-zinc-900 text-zinc-400">
            <tr>
              <th className="text-left px-4 py-3">Nombre</th>
              <th className="text-left px-4 py-3">Ciudad</th>
              <th className="text-left px-4 py-3">Estado</th>
              <th className="text-left px-4 py-3">Premium</th>
              <th className="text-left px-4 py-3">Registrado</th>
              <th className="text-right px-4 py-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {(users ?? []).map((user) => (
              <tr key={user.id} className="border-t border-zinc-800">
                <td className="px-4 py-3">{user.display_name}</td>
                <td className="px-4 py-3 text-zinc-400">{user.city ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`inline-block rounded-full border px-2 py-0.5 text-xs ${STATUS_STYLES[user.status]}`}>
                    {user.status}
                  </span>
                </td>
                <td className="px-4 py-3">{user.is_premium ? '⭐' : '—'}</td>
                <td className="px-4 py-3 text-zinc-400">{new Date(user.created_at).toLocaleDateString('es-ES')}</td>
                <td className="px-4 py-3 text-right space-x-2">
                  {user.status !== 'suspended' ? (
                    <form action={setUserStatus.bind(null, user.id, 'suspended')} className="inline">
                      <button className="text-xs text-rose-400 hover:text-rose-300">Suspender</button>
                    </form>
                  ) : (
                    <form action={setUserStatus.bind(null, user.id, 'active')} className="inline">
                      <button className="text-xs text-emerald-400 hover:text-emerald-300">Reactivar</button>
                    </form>
                  )}
                  {user.status !== 'deleted' ? (
                    <form action={setUserStatus.bind(null, user.id, 'deleted')} className="inline">
                      <button className="text-xs text-zinc-500 hover:text-zinc-300">Eliminar</button>
                    </form>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
