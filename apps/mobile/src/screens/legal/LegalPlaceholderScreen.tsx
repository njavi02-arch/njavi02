import React from 'react';
import { ScrollView, Text, View } from 'react-native';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';

interface LegalPlaceholderScreenProps {
  title: string;
  lastUpdatedNote: string;
  sections: { heading: string; body: string }[];
}

/**
 * Plantilla para Términos de Servicio y Política de Privacidad. El CONTENIDO es un
 * placeholder deliberado — no se redactan textos legales definitivos porque eso requiere
 * revisión de un profesional (ver docs/06-security-and-privacy.md §6). Lo que sí es real
 * es la estructura: las secciones que un documento de este tipo necesita cubrir para una
 * app social con geolocalización aproximada, chat, pagos y usuarios en la UE.
 */
export function LegalPlaceholderScreen({ title, lastUpdatedNote, sections }: LegalPlaceholderScreenProps) {
  const theme = useTheme();

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text
          style={{
            fontFamily: theme.typography.fontFamilyHeading,
            fontSize: theme.typography.sizes.h1,
            color: theme.colors.textPrimary,
            marginBottom: theme.spacing.xxs,
          }}
        >
          {title}
        </Text>
        <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption, marginBottom: theme.spacing.md }}>
          {lastUpdatedNote}
        </Text>

        <View
          style={{
            backgroundColor: theme.colors.surface,
            borderRadius: theme.radius.md,
            borderWidth: 1,
            borderColor: theme.colors.warning,
            padding: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          <Text style={{ color: theme.colors.warning, fontFamily: theme.typography.fontFamilyBodySemibold }}>
            ⚠️ Pendiente de revisión legal
          </Text>
          <Text style={{ color: theme.colors.textSecondary, marginTop: theme.spacing.xxs }}>
            Este texto es un borrador estructural, no un documento legal válido. No publicar
            la app sin que un profesional del derecho lo revise y complete.
          </Text>
        </View>

        {sections.map((section) => (
          <View key={section.heading} style={{ marginBottom: theme.spacing.md }}>
            <Text
              style={{
                color: theme.colors.textPrimary,
                fontFamily: theme.typography.fontFamilyHeadingSemibold,
                fontSize: theme.typography.sizes.h3,
                marginBottom: theme.spacing.xxs,
              }}
            >
              {section.heading}
            </Text>
            <Text style={{ color: theme.colors.textSecondary, lineHeight: 20 }}>{section.body}</Text>
          </View>
        ))}
      </ScrollView>
    </ScreenContainer>
  );
}
