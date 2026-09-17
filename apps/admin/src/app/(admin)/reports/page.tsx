import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { actionReportAndSuspend, setReportStatus } from './actions';

const REASON_LABELS: Record<string, string> = {
  spam: 'Spam',
  fake_profile: 'Perfil falso',
  inappropriate_content: 'Contenido inapropiado',
  harassment: 'Acoso',
  underage: 'Menor de edad',
  other: 'Otro',
};

interface PendingReport {
  id: string;
  reason: string;
  details: string | null;
  status: string;
  created_at: string;
  reporter: { id: string; display_name: string } | null;
  reported: { id: string; display_name: string; status: string } | null;
}

export default async function ReportsPage() {
  const { data: reports, error } = await supabaseAdmin
    .from('reports')
    .select(
      `id, reason, details, status, created_at,
       reporter:profiles!reports_reporter_id_fkey(id, display_name),
       reported:profiles!reports_reported_id_fkey(id, display_name, status)`,
    )
    .eq('status', 'pending')
    .order('created_at', { ascending: false })
    .limit(50);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Reportes pendientes</h1>
      {error ? <p className="text-rose-400">{error.message}</p> : null}

      {(reports ?? []).length === 0 ? (
        <p className="text-zinc-500">No hay reportes pendientes. 🎉</p>
      ) : null}

      <div className="flex flex-col gap-3">
        {((reports ?? []) as unknown as PendingReport[]).map((report) => (
          <div key={report.id} className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="rounded-full bg-rose-950 text-rose-400 border border-rose-800 px-2 py-0.5 text-xs">
                {REASON_LABELS[report.reason] ?? report.reason}
              </span>
              <span className="text-xs text-zinc-500">{new Date(report.created_at).toLocaleString('es-ES')}</span>
            </div>
            <p className="text-sm mb-1">
              <span className="text-zinc-400">Reportado:</span> {report.reported?.display_name} ({report.reported?.status})
            </p>
            <p className="text-sm mb-1">
              <span className="text-zinc-400">Denunciante:</span> {report.reporter?.display_name}
            </p>
            {report.details ? (
              <p className="text-sm text-zinc-300 mt-2 italic">&quot;{report.details}&quot;</p>
            ) : null}

            <div className="flex gap-3 mt-3">
              <form action={actionReportAndSuspend.bind(null, report.id, report.reported?.id ?? '')}>
                <button className="text-xs rounded-full bg-rose-500 hover:bg-rose-400 text-white px-3 py-1.5">
                  Suspender usuario
                </button>
              </form>
              <form action={setReportStatus.bind(null, report.id, 'dismissed')}>
                <button className="text-xs rounded-full border border-zinc-700 hover:border-zinc-500 px-3 py-1.5">
                  Descartar
                </button>
              </form>
              <form action={setReportStatus.bind(null, report.id, 'reviewed')}>
                <button className="text-xs rounded-full border border-zinc-700 hover:border-zinc-500 px-3 py-1.5">
                  Marcar revisado
                </button>
              </form>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
