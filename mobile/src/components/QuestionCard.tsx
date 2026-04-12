import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, font, radius, spacing } from '../theme';

interface Props {
  question: string;
  systemTag?: string | null;
  topicTag?: string | null;
}

export function QuestionCard({ question, systemTag, topicTag }: Props) {
  return (
    <View style={styles.card}>
      {(systemTag || topicTag) && (
        <View style={styles.tagRow}>
          {systemTag && <Text style={styles.tag}>{systemTag}</Text>}
          {topicTag && <Text style={styles.tag}>{topicTag}</Text>}
        </View>
      )}
      <Text style={styles.question}>{question}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  tagRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  tag: {
    fontSize: font.xs,
    color: colors.primary,
    backgroundColor: '#1D3461',
    paddingVertical: 2,
    paddingHorizontal: spacing.sm,
    borderRadius: radius.full,
    overflow: 'hidden',
  },
  question: {
    fontSize: font.lg,
    color: colors.textPrimary,
    lineHeight: 28,
    fontWeight: '500',
  },
});
