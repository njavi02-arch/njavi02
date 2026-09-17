import { LoginForm } from './LoginForm';
import { isAdminBackendConfigured } from '@/lib/supabaseAdmin';

export default function LoginPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-black px-4">
      <div className="text-center mb-8">
        <div className="text-4xl mb-2">🪐</div>
        <h1 className="text-2xl font-bold text-white">Orbita — Panel admin</h1>
      </div>

      {!isAdminBackendConfigured ? (
        <p className="text-sm text-amber-400 max-w-sm text-center mb-4">
          SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY no configuradas todavía. Copia
          .env.example a .env.local y añade las credenciales de tu proyecto Supabase.
        </p>
      ) : null}

      <LoginForm />
    </main>
  );
}
