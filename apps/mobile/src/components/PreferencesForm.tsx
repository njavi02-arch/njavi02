import React, { useState } from 'react';
import { Text, View, ScrollView, Switch } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { TextField } from './TextField';
import { HashtagSelector } from './HashtagSelector';

interface UserPreferences {
  min_age: number;
  max_age: number;
  gender_preference: string[];
  max_distance_km: number;
  preferred_hashtags: string[];
  show_verified_only: boolean;
}

interface PreferencesFormProps {
  preferences: UserPreferences;
  onChange: (preferences: UserPreferences) => void;
  isLoading?: boolean;
}

const GENDER_OPTIONS = ['female', 'male', 'couple'];

export function PreferencesForm({ preferences, onChange, isLoading }: PreferencesFormProps) {
  const theme = useTheme();

  const updateField = (key: keyof UserPreferences, value: any) => {
    onChange({ ...preferences, [key]: value });
  };

  return (
    <ScrollView contentContainerStyle={{ paddingBottom: theme.spacing.xl }}>
      <View style={{ paddingHorizontal: theme.spacing.md }}>
        {/* Age Range */}
        <View style={{ marginBottom: theme.spacing.lg }}>
          <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: theme.colors.textPrimary, marginBottom: theme.spacing.sm }}>
            Rango de edad
          </Text>
          <View style={{ flexDirection: 'row', gap: theme.spacing.md }}>
            <View style={{ flex: 1 }}>
              <TextField
                label="Mín"
                value={String(preferences.min_age)}
                onChangeText={(text) => updateField('min_age', parseInt(text) || 18)}
                keyboardType="numeric"
                disabled={isLoading}
              />
            </View>
            <View style={{ flex: 1 }}>
              <TextField
                label="Máx"
                value={String(preferences.max_age)}
                onChangeText={(text) => updateField('max_age', parseInt(text) || 65)}
                keyboardType="numeric"
                disabled={isLoading}
              />
            </View>
          </View>
        </View>

        {/* Distance */}
        <View style={{ marginBottom: theme.spacing.lg }}>
          <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: theme.colors.textPrimary, marginBottom: theme.spacing.sm }}>
            Distancia máxima (km)
          </Text>
          <TextField
            label="25"
            value={String(preferences.max_distance_km)}
            onChangeText={(text) => updateField('max_distance_km', parseInt(text) || 50)}
            keyboardType="numeric"
            disabled={isLoading}
          />
        </View>

        {/* Gender Preference */}
        <View style={{ marginBottom: theme.spacing.lg }}>
          <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: theme.colors.textPrimary, marginBottom: theme.spacing.sm }}>
            Género preferido
          </Text>
          <View style={{ flexDirection: 'row', gap: theme.spacing.sm }}>
            {GENDER_OPTIONS.map((gender) => {
              const isSelected = preferences.gender_preference.includes(gender);
              const labels: Record<string, string> = {
                female: '👩 Mujer',
                male: '👨 Hombre',
                couple: '👫 Pareja',
              };
              return (
                <View
                  key={gender}
                  style={{
                    flex: 1,
                    paddingHorizontal: theme.spacing.sm,
                    paddingVertical: theme.spacing.xs,
                    borderRadius: theme.radius.md,
                    backgroundColor: isSelected ? theme.colors.primary : theme.colors.surface,
                    borderWidth: 1,
                    borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                  }}
                >
                  <Text
                    style={{
                      textAlign: 'center',
                      fontFamily: theme.typography.fontFamilyBody,
                      fontSize: 12,
                      color: isSelected ? '#fff' : theme.colors.textPrimary,
                    }}
                  >
                    {labels[gender]}
                  </Text>
                </View>
              );
            })}
          </View>
        </View>

        {/* Hashtags */}
        <View style={{ marginBottom: theme.spacing.lg }}>
          <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: theme.colors.textPrimary, marginBottom: theme.spacing.sm }}>
            Hashtags de interés
          </Text>
          <HashtagSelector
            selected={preferences.preferred_hashtags}
            onChange={(tags) => updateField('preferred_hashtags', tags)}
            maxTags={10}
          />
        </View>

        {/* Verified Only */}
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: theme.spacing.md, borderTopWidth: 1, borderTopColor: theme.colors.border }}>
          <Text style={{ fontFamily: theme.typography.fontFamilyBody, fontSize: 14, color: theme.colors.textPrimary }}>
            Solo perfiles verificados
          </Text>
          <Switch
            value={preferences.show_verified_only}
            onValueChange={(value) => updateField('show_verified_only', value)}
            disabled={isLoading}
          />
        </View>
      </View>
    </ScrollView>
  );
}
