'use client';

import { useActionState } from 'react';
import { updateConfigValue, type UpdateConfigState } from './actions';

const initialState: UpdateConfigState = { error: null, success: false };

export function ConfigRow({
  configKey,
  description,
  value,
}: {
  configKey: string;
  description: string | null;
  value: unknown;
}) {
  const boundAction = updateConfigValue.bind(null, configKey);
  const [state, formAction, pending] = useActionState(boundAction, initialState);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
      <div className="flex items-baseline justify-between mb-1">
        <code className="text-sm font-semibold text-rose-300">{configKey}</code>
        {state.success ? <span className="text-xs text-emerald-400">Guardado ✓</span> : null}
      </div>
      {description ? <p className="text-xs text-zinc-500 mb-2">{description}</p> : null}
      <form action={formAction} className="flex flex-col gap-2">
        <textarea
          name="value"
          defaultValue={JSON.stringify(value, null, 2)}
          rows={value && typeof value === 'object' ? 6 : 1}
          className="w-full rounded-lg bg-black border border-zinc-700 px-3 py-2 font-mono text-xs text-zinc-100 outline-none focus:border-rose-400"
        />
        {state.error ? <p className="text-xs text-rose-400">{state.error}</p> : null}
        <button
          type="submit"
          disabled={pending}
          className="self-start text-xs rounded-full bg-zinc-100 text-black px-3 py-1.5 hover:bg-white disabled:opacity-50"
        >
          {pending ? 'Guardando…' : 'Guardar'}
        </button>
      </form>
    </div>
  );
}
