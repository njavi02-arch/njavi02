import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { computePhotoVisibility } from '@orbita/shared';
import type { AppConfig } from '@orbita/shared';

interface PhotoGalleryProps {
  photos: { url: string; position: number }[];
  config: Pick<AppConfig, 'public_photos_count'>;
  isUnlocked: boolean;
  onPressLocked?: () => void;
}

export function PhotoGallery({ photos, config, isUnlocked, onPressLocked }: PhotoGalleryProps) {
  const theme = useTheme();
  const sorted = [...photos].sort((a, b) => a.position - b.position);
  const visibility = computePhotoVisibility(sorted.length, config, isUnlocked);
  const visiblePhotos = isUnlocked ? sorted : sorted.slice(0, visibility.publicCount);

  return (
    <View style={styles.grid}>
      {visiblePhotos.map((photo) => (
        <Image key={photo.position} source={{ uri: photo.url }} style={[styles.cell, { borderRadius: theme.radius.sm }]} />
      ))}
      {visibility.lockedBadgeLabel ? (
        <Pressable
          onPress={onPressLocked}
          style={[
            styles.cell,
            styles.lockedCell,
            { borderRadius: theme.radius.sm, backgroundColor: theme.colors.surfaceElevated },
          ]}
        >
          <Text style={{ fontSize: 22 }}>🔒</Text>
          <Text
            style={{
              color: theme.colors.textPrimary,
              fontFamily: theme.typography.fontFamilyBodySemibold,
              fontSize: theme.typography.sizes.bodySmall,
              marginTop: 4,
              textAlign: 'center',
            }}
          >
            {visibility.lockedBadgeLabel}
          </Text>
        </Pressable>
      ) : null}
    </View>
  );
}

const CELL_SIZE = '31%';

const styles = StyleSheet.create({
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  cell: { width: CELL_SIZE, aspectRatio: 0.8, marginBottom: 12 },
  lockedCell: { alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderStyle: 'dashed' },
});
