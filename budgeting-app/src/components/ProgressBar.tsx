import React from 'react';
import { StyleSheet, View } from 'react-native';
import { colors, radius } from '../constants/theme';

interface Props {
  progress: number; // 0..1+ (can exceed 1 when over budget)
  color?: string;
  overColor?: string;
  height?: number;
}

export function ProgressBar({ progress, color = colors.primary, overColor = colors.danger, height = 8 }: Props) {
  const clamped = Math.max(0, Math.min(progress, 1));
  const isOver = progress > 1;
  return (
    <View style={[styles.track, { height }]}>
      <View
        style={[
          styles.fill,
          {
            width: `${clamped * 100}%`,
            backgroundColor: isOver ? overColor : color,
            height,
          },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    width: '100%',
    backgroundColor: colors.border,
    borderRadius: radius.sm,
    overflow: 'hidden',
  },
  fill: {
    borderRadius: radius.sm,
  },
});
