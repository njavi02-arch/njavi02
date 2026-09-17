import { describe, expect, it } from 'vitest';
import { PROMPT_QUESTIONS, suggestIcebreakers } from './icebreakers';

describe('suggestIcebreakers', () => {
  it('con interés compartido, sugiere una apertura que lo menciona', () => {
    const result = suggestIcebreakers('Laura', ['Viajar', 'Fotografía'], []);
    expect(result[0].source).toBe('shared_interest');
    expect(result[0].text).toContain('Viajar');
    expect(result[0].text).toContain('Laura');
  });

  it('con un prompt de la otra persona, sugiere referenciarlo', () => {
    const result = suggestIcebreakers('Marcos', [], [{ question: '¿Mi cita ideal?', answer: 'Cine y palomitas' }]);
    expect(result.some((s) => s.source === 'prompt' && s.text.includes('Cine y palomitas'))).toBe(true);
  });

  it('sin intereses ni prompts, cae a una apertura genérica (nunca se queda vacío)', () => {
    const result = suggestIcebreakers('Ana', [], []);
    expect(result.length).toBeGreaterThan(0);
    expect(result[0].source).toBe('generic');
  });

  it('nunca sugiere más de 3 opciones', () => {
    const result = suggestIcebreakers('Ana', ['Música', 'Cine'], [{ question: 'q', answer: 'a' }]);
    expect(result.length).toBeLessThanOrEqual(3);
  });
});

describe('PROMPT_QUESTIONS', () => {
  it('tiene al menos 3 preguntas disponibles para elegir (el perfil permite hasta 3 prompts)', () => {
    expect(PROMPT_QUESTIONS.length).toBeGreaterThanOrEqual(3);
  });

  it('no tiene preguntas duplicadas', () => {
    expect(new Set(PROMPT_QUESTIONS).size).toBe(PROMPT_QUESTIONS.length);
  });
});
