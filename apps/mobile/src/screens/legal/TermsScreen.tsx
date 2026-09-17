import React from 'react';
import { LegalPlaceholderScreen } from './LegalPlaceholderScreen';

export function TermsScreen() {
  return (
    <LegalPlaceholderScreen
      title="Términos de Servicio"
      lastUpdatedNote="Borrador — sin fecha de publicación"
      sections={[
        {
          heading: '1. Quién puede usar Orbita',
          body:
            'Edad mínima: 18 años (verificada por fecha de nacimiento en el registro, ' +
            'no autodeclaración). [PENDIENTE: confirmar si se requiere alguna verificación ' +
            'adicional de edad según la jurisdicción de lanzamiento.]',
        },
        {
          heading: '2. Naturaleza del servicio',
          body:
            'Orbita es una app social de descubrimiento y conversación entre personas. No ' +
            'garantiza la identidad, intenciones ni veracidad de la información de otros ' +
            'usuarios. [PENDIENTE: cláusula de exención de responsabilidad sobre encuentros ' +
            'en persona, redactada por un profesional.]',
        },
        {
          heading: '3. Conducta del usuario',
          body:
            'Prohibido: acoso, suplantación de identidad, spam, contenido ilegal o de ' +
            'menores, uso de la app para fines distintos a los previstos. Ver el sistema de ' +
            'reportes y bloqueos en la app. [PENDIENTE: listado legal completo de conductas ' +
            'prohibidas y consecuencias contractuales.]',
        },
        {
          heading: '4. Contenido generado por el usuario',
          body:
            'El usuario es responsable de las fotos, bio y mensajes que publica. Orbita ' +
            'puede moderar, ocultar o eliminar contenido que incumpla estos términos. ' +
            '[PENDIENTE: licencia de uso del contenido, retención tras eliminación de cuenta.]',
        },
        {
          heading: '5. Monedas, Super Likes y suscripción Premium',
          body:
            'Son elementos consumibles/de suscripción sin valor monetario fuera de la app. ' +
            '[PENDIENTE: política de reembolsos, condiciones de facturación recurrente — ' +
            'debe alinearse con los requisitos de Apple/Google al conectar la pasarela de pago real.]',
        },
        {
          heading: '6. Suspensión y cierre de cuenta',
          body:
            'Orbita puede suspender cuentas que incumplan estos términos, especialmente tras ' +
            'reportes de acoso o sospecha de minoría de edad. El usuario puede eliminar su ' +
            'cuenta en cualquier momento desde Ajustes. [PENDIENTE: plazos y proceso de apelación.]',
        },
        {
          heading: '7. Ley aplicable y jurisdicción',
          body: '[PENDIENTE: a determinar por el equipo legal según el país de constitución de la empresa.]',
        },
      ]}
    />
  );
}
