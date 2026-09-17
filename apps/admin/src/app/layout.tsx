import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Orbita — Panel de administración',
  description: 'Gestión de usuarios, moderación y configuración de Orbita',
};

export default function RootLayout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
