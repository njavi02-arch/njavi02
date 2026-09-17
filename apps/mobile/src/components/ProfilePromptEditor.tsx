import React, { useState } from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import { PROMPT_QUESTIONS } from '@orbita/shared';
import { useTheme } from '../theme/ThemeProvider';
import { Chip } from './Chip';
import { TextField } from './TextField';
import { Button } from './Button';
import { deleteProfilePrompt, upsertProfilePrompt } from '../services/profiles';
import type { ProfilePromptRow } from '../types/database';

interface ProfilePromptEditorProps {
  profileId: string;
  position: number;
  existing: ProfilePromptRow | null;
  onChanged: () => void;
}

/** Un slot de prompt de perfil (hasta 3 por perfil, ver
 * supabase/migrations/0005_verification_prompts_boost_flags.sql). Elegir pregunta +
 * escribir respuesta + guardar, o borrar el prompt entero. */
export function ProfilePromptEditor({ profileId, position, existing, onChanged }: ProfilePromptEditorProps) {
  const theme = useTheme();
  const [question, setQuestion] = useState(existing?.question ?? '');
  const [answer, setAnswer] = useState(existing?.answer ?? '');
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    if (!question || answer.trim().length === 0) return;
    setSaving(true);
    try {
      await upsertProfilePrompt(profileId, position, question, answer.trim());
      onChanged();
    } catch (e) {
      Alert.alert('No se pudo guardar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setSaving(false);
    }
  }

  async function handleClear() {
    if (!existing) {
      setQuestion('');
      setAnswer('');
      return;
    }
    try {
      await deleteProfilePrompt(existing.id);
      setQuestion('');
      setAnswer('');
      onChanged();
    } catch (e) {
      Alert.alert('No se pudo borrar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    }
  }

  return (
    <View style={{ backgroundColor: theme.colors.surface, borderRadius: theme.radius.md, padding: theme.spacing.sm, marginBottom: theme.spacing.sm }}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: theme.spacing.xs }}>
        <View style={{ flexDirection: 'row' }}>
          {PROMPT_QUESTIONS.map((q) => (
            <Chip key={q} label={q} selected={question === q} onPress={() => setQuestion(q)} />
          ))}
        </View>
      </ScrollView>
      {question ? (
        <>
          <TextField
            placeholder="Tu respuesta..."
            value={answer}
            onChangeText={setAnswer}
            maxLength={200}
            style={{ marginBottom: 0 }}
          />
          <View style={{ flexDirection: 'row', marginTop: theme.spacing.xs }}>
            {existing ? (
              <Button label="Borrar" variant="ghost" fullWidth={false} onPress={handleClear} style={{ marginRight: 8 }} />
            ) : null}
            <View style={{ flex: 1 }}>
              <Button label="Guardar" onPress={handleSave} disabled={answer.trim().length === 0} loading={saving} />
            </View>
          </View>
        </>
      ) : (
        <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
          Elige una pregunta para este prompt
        </Text>
      )}
    </View>
  );
}
