import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { moderatePhoto } from './actions';

export default async function PhotosPage() {
  const { data: photos, error } = await supabaseAdmin
    .from('photos')
    .select('id, url, position, created_at, profile:profiles!photos_profile_id_fkey(display_name)')
    .eq('moderation_status', 'pending')
    .order('created_at', { ascending: true })
    .limit(60);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Moderación de fotos</h1>
      {error ? <p className="text-rose-400">{error.message}</p> : null}

      {(photos ?? []).length === 0 ? <p className="text-zinc-500">No hay fotos pendientes de revisión. 🎉</p> : null}

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {(photos ?? []).map((photo: any) => (
          <div key={photo.id} className="rounded-xl overflow-hidden border border-zinc-800 bg-zinc-900">
            <div className="relative w-full aspect-[3/4] bg-zinc-800">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={photo.url} alt="" className="w-full h-full object-cover" />
            </div>
            <div className="p-2">
              <p className="text-xs text-zinc-400 truncate mb-2">{photo.profile?.display_name}</p>
              <div className="flex gap-2">
                <form action={moderatePhoto.bind(null, photo.id, 'approved')} className="flex-1">
                  <button className="w-full text-xs rounded-full bg-emerald-600 hover:bg-emerald-500 text-white py-1.5">
                    Aprobar
                  </button>
                </form>
                <form action={moderatePhoto.bind(null, photo.id, 'rejected')} className="flex-1">
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
