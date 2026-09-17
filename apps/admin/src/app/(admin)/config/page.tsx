import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { ConfigRow } from './ConfigRow';

export default async function ConfigPage() {
  const { data: config, error } = await supabaseAdmin.from('app_config').select('*').order('key');

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Configuración</h1>
      <p className="text-sm text-zinc-500 mb-6">
        Todas las cifras de negocio de Orbita (mensajes gratuitos, precios, límites,
        recompensas) viven aquí — nunca están escritas directamente en el código de la
        app ni del panel. Los cambios se aplican de inmediato.
      </p>
      {error ? <p className="text-rose-400">{error.message}</p> : null}

      <div className="grid md:grid-cols-2 gap-4">
        {(config ?? []).map((row) => (
          <ConfigRow key={row.key} configKey={row.key} description={row.description} value={row.value} />
        ))}
      </div>
    </div>
  );
}
