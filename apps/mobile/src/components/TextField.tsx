import React from 'react';
import { StyleSheet, Text, TextInput, View, type TextInputProps } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

interface TextFieldProps extends TextInputProps {
  label?: string;
  error?: string;
  multiline?: boolean;
}

export function TextField({ label, error, style, multiline, ...rest }: TextFieldProps) {
  const theme = useTheme();

  return (
    <View style={{ marginBottom: theme.spacing.md }}>
      {label ? (
        <Text
          style={{
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamilyBodyMedium,
            fontSize: theme.typography.sizes.bodySmall,
            marginBottom: theme.spacing.xxs,
          }}
        >
          {label}
        </Text>
      ) : null}
      <TextInput
        placeholderTextColor={theme.colors.textSecondary}
        style={[
          styles.input,
          {
            backgroundColor: theme.colors.surface,
            borderColor: error ? theme.colors.danger : theme.colors.border,
            color: theme.colors.textPrimary,
            borderRadius: theme.radius.sm,
            fontFamily: theme.typography.fontFamilyBody,
            minHeight: multiline ? 96 : 48,
            textAlignVertical: multiline ? 'top' : 'center',
          },
          style,
        ]}
        multiline={multiline}
        {...rest}
      />
      {error ? (
        <Text style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.caption, marginTop: 4 }}>
          {error}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
  },
});
