import 'server-only';
import { createHmac, timingSafeEqual } from 'crypto';

const COOKIE_NAME = 'orbita_admin_session';
const SESSION_TTL_MS = 12 * 60 * 60 * 1000; // 12 horas

function getSecret(): string {
  const secret = process.env.ADMIN_SESSION_SECRET;
  if (!secret) {
    throw new Error('ADMIN_SESSION_SECRET no está configurado (ver apps/admin/.env.example)');
  }
  return secret;
}

function sign(payload: string): string {
  return createHmac('sha256', getSecret()).update(payload).digest('hex');
}

/** Crea el valor de cookie firmado: "<adminUserId>.<expiresAtMs>.<hmac>" — evita que un
 * usuario pueda fabricar o alterar la cookie para suplantar a otro admin. */
export function createSessionCookieValue(adminUserId: string): string {
  const expiresAt = Date.now() + SESSION_TTL_MS;
  const payload = `${adminUserId}.${expiresAt}`;
  return `${payload}.${sign(payload)}`;
}

export function verifySessionCookieValue(value: string | undefined): string | null {
  if (!value) return null;
  const parts = value.split('.');
  if (parts.length !== 3) return null;
  const [adminUserId, expiresAtRaw, signature] = parts;
  const payload = `${adminUserId}.${expiresAtRaw}`;
  const expected = sign(payload);

  const a = Buffer.from(signature);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;

  const expiresAt = Number(expiresAtRaw);
  if (!Number.isFinite(expiresAt) || Date.now() > expiresAt) return null;

  return adminUserId;
}

export const ADMIN_SESSION_COOKIE = COOKIE_NAME;
