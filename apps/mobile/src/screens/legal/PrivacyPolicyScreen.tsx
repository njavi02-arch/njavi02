import React from 'react';
import { LegalPlaceholderScreen } from './LegalPlaceholderScreen';

export function PrivacyPolicyScreen() {
  return (
    <LegalPlaceholderScreen
      title="Política de Privacidad"
      lastUpdatedNote="Borrador — sin fecha de publicación"
      sections={[
        {
          heading: '1. Qué datos recogemos',
          body:
            'Datos de perfil (nombre, fecha de nacimiento, género, ciudad, bio, fotos, ' +
            'intereses), datos de uso (mensajes, vistas de perfil, Super Likes), y datos ' +
            'técnicos mínimos para seguridad (hash de dispositivo/IP para detección de ' +
            'cuentas duplicadas — nunca la IP en claro, ver docs/06-security-and-privacy.md).',
        },
        {
          heading: '2. Base legal del tratamiento (RGPD)',
          body:
            'Ejecución del contrato (prestar el servicio), consentimiento (notificaciones ' +
            'de marketing, gestionable por separado en Ajustes) e interés legítimo ' +
            '(seguridad, prevención de fraude). [PENDIENTE: confirmación formal por un DPO/' +
            'asesoría legal antes de publicar.]',
        },
        {
          heading: '3. Con quién compartimos datos',
          body:
            'Proveedores de infraestructura (Supabase: base de datos, autenticación, ' +
            'almacenamiento de imágenes) bajo su propio acuerdo de tratamiento de datos. ' +
            'No vendemos datos personales a terceros. [PENDIENTE: listado completo de ' +
            'subencargados y sus DPA firmados antes de producción.]',
        },
        {
          heading: '4. Ubicación',
          body:
            'Guardamos ciudad y coordenadas aproximadas, nunca localización GPS continua. ' +
            'El usuario controla si comparte ubicación durante el onboarding.',
        },
        {
          heading: '5. Tus derechos',
          body:
            'Acceso, rectificación, supresión ("derecho al olvido" — eliminar cuenta desde ' +
            'Ajustes ejecuta un borrado y anonimización, ver docs/03-database.md §2), ' +
            'portabilidad y oposición. [PENDIENTE: construir el endpoint de exportación de ' +
            'datos — el modelo de datos ya lo soporta, ver docs/07-roadmap-and-scaling.md.]',
        },
        {
          heading: '6. Retención de datos',
          body:
            '[PENDIENTE: definir plazos concretos de retención tras eliminación de cuenta y ' +
            'tras cierre de una cuenta suspendida, con el equipo legal.]',
        },
        {
          heading: '7. Menores de edad',
          body:
            'Orbita no admite usuarios menores de 18 años. Si detectamos una cuenta de un ' +
            'menor, se suspende y elimina. Ver el motivo de reporte "Menor de edad" en la app.',
        },
        {
          heading: '8. Contacto',
          body: '[PENDIENTE: dirección de contacto del responsable del tratamiento y, si aplica, del DPO.]',
        },
      ]}
    />
  );
}
