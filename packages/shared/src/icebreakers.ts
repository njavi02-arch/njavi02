// Prompts de perfil + sugerencias de primer mensaje — ver PRODUCT_BRAIN.md →
// INVESTIGACIÓN (Hinge/Bumble) y DECISIONES: resolvemos el mismo problema ("no sé qué
// escribir") con preguntas curadas + sugerencias por interés compartido, sin depender de
// un servicio de IA generativa de pago externo.

/** Catálogo de preguntas de prompt que un usuario puede elegir para su perfil (máximo 3,
 * ver profile_prompts en supabase/migrations/0005_*.sql). Genéricas y propias — no son
 * copia literal de ninguna app concreta. */
export const PROMPT_QUESTIONS: string[] = [
  'Mi cita/plan ideal sería...',
  'No puedo vivir sin...',
  'Pregúntame sobre...',
  'Un dato random sobre mí...',
  'La mejor forma de conquistarme es...',
  'Mi playlist ahora mismo es puro...',
  'Nunca podría salir con alguien que...',
  'El próximo viaje que quiero hacer es a...',
  'Mi serie/película favorita es... porque...',
  'Algo que me haría reír seguro...',
];

export interface ProfilePromptLike {
  question: string;
  answer: string;
}

export interface IcebreakerSuggestion {
  text: string;
  /** De dónde sale la sugerencia, para poder explicarlo en la UI si hace falta. */
  source: 'shared_interest' | 'prompt' | 'generic';
}

const GENERIC_OPENERS = ['Hola, ¿qué tal? 👋', '¡Hola! ¿Qué tal el día?'];

/**
 * Sugiere un puñado de posibles primeros mensajes a partir de los intereses compartidos y
 * los prompts de la otra persona. Puramente determinista (sin IA) — el usuario siempre
 * puede escribir su propio mensaje; esto es solo para reducir la fricción de la página en
 * blanco, el mismo problema que Bumble/Hinge resuelven con Icebreaker/Opening Move.
 */
export function suggestIcebreakers(
  otherDisplayName: string,
  sharedInterests: string[],
  otherPrompts: ProfilePromptLike[],
): IcebreakerSuggestion[] {
  const suggestions: IcebreakerSuggestion[] = [];

  if (sharedInterests.length > 0) {
    const interest = sharedInterests[0];
    suggestions.push({
      text: `Hola ${otherDisplayName}, veo que también te gusta ${interest} — ¿desde cuándo?`,
      source: 'shared_interest',
    });
  }

  if (otherPrompts.length > 0) {
    const prompt = otherPrompts[0];
    suggestions.push({
      text: `${prompt.question} — me ha encantado tu respuesta ("${prompt.answer}"), ¡cuéntame más!`,
      source: 'prompt',
    });
  }

  if (suggestions.length === 0) {
    suggestions.push({ text: `${GENERIC_OPENERS[0].replace('Hola,', `Hola ${otherDisplayName},`)}`, source: 'generic' });
  }

  return suggestions.slice(0, 3);
}
