import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { reviewVerification } from './actions';

interface PendingVerification {
  id: string;
  selfie_url: string;
  created_at: string;
  profile: { display_name: string } | null;
}

export default async function VerificationsPage() {
  const { data: requests, error } = await supabaseAdmin
    .from('verification_requests')
    .select('id, selfie_url, created_at, profile:profiles!verification_requests_profile_id_fkey(display_name)')
    .eq('status', 'pending')
    .order('created_at', { ascending: true })
    .limit(60);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Verificación de perfiles</h1>
      <p className="text-sm text-zinc-500 mb-6">
        Compara la selfie con las fotos del perfil del usuario antes de aprobar. Al aprobar,
        el perfil recibe el badge ✅ de inmediato.
      </p>
      {error ? <p className="text-rose-400">{error.message}</p> : null}

      {(requests ?? []).length === 0 ? <p className="text-zinc-500">No hay solicitudes pendientes. 🎉</p> : null}

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {((requests ?? []) as unknown as PendingVerification[]).map((req) => (
          <div key={req.id} className="rounded-xl overflow-hidden border border-zinc-800 bg-zinc-900">
            <div className="relative w-full aspect-[3/4] bg-zinc-800">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={req.selfie_url} alt="" className="w-full h-full object-cover" />
            </div>
            <div className="p-2">
              <p className="text-xs text-zinc-400 truncate mb-2">{req.profile?.display_name}</p>
              <div className="flex gap-2">
                <form action={reviewVerification.bind(null, req.id, 'approved', undefined)} className="flex-1">
                  <button className="w-full text-xs rounded-full bg-emerald-600 hover:bg-emerald-500 text-white py-1.5">
                    Aprobar
                  </button>
                </form>
                <form action={reviewVerification.bind(null, req.id, 'rejected', 'No coincide con las fotos del perfil')} className="flex-1">
                  <button className="w-full text-xs rounded-full bg-rose-600 hover:bg-rose-500 text-white py-1.5">
                    Rechazar
                  </button>
                </form>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
