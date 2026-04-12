import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { mastery as masteryColors, colors, radius, spacing, font } from '../theme';

type Mastery = 'weak' | 'fragile' | 'developing' | 'strong';

const LABELS: Record<Mastery, string> = {
  weak: 'Weak',
  fragile: 'Fragile',
  developing: 'Developing',
  strong: 'Strong',
};

const EMOJI: Record<Mastery, string> = {
  weak: '✗',
  fragile: '△',
  developing: '◑',
  strong: '✓',
};

interface Props {
  level: Mastery;
}

export function MasteryBadge({ level }: Props) {
  const color = masteryColors[level];
  return (
    <View style={[styles.badge, { borderColor: color }]}>
      <Text style={[styles.emoji, { color }]}>{EMOJI[level]}</Text>
      <Text style={[styles.label, { color }]}>{LABELS[level]}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: radius.full,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.sm,
    gap: spacing.xs,
    alignSelf: 'flex-start',
  },
  emoji: { fontSize: font.sm, fontWeight: '700' },
  label: { fontSize: font.sm, fontWeight: '600' },
});
