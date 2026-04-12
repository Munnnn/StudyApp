import React, { useCallback, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { getDashboard, Dashboard } from '../api/endpoints';
import { MasteryBadge } from '../components/MasteryBadge';
import { colors, font, radius, spacing } from '../theme';

function StatBox({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
      {sub && <Text style={styles.statSub}>{sub}</Text>}
    </View>
  );
}

export function DashboardScreen() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useFocusEffect(useCallback(() => {
    setLoading(true);
    getDashboard().then(setData).finally(() => setLoading(false));
  }, []));

  if (loading) {
    return <View style={styles.center}><ActivityIndicator color={colors.primary} /></View>;
  }

  if (!data) return null;

  const { mastery_distribution: md } = data;
  const totalDist = md.weak + md.fragile + md.developing + md.strong || 1;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      <Text style={styles.heading}>Progress</Text>

      {/* Summary stats */}
      <View style={styles.statRow}>
        <StatBox label="Total attempts" value={data.total_attempts} />
        <StatBox label="Cards studied" value={`${data.cards_studied}/${data.cards_total}`} />
        <StatBox label="Strong" value={data.strong_mastery_count} />
      </View>

      {/* Mastery bar */}
      <Text style={styles.sectionLabel}>MASTERY DISTRIBUTION</Text>
      <View style={styles.barContainer}>
        {(['weak', 'fragile', 'developing', 'strong'] as const).map(level => {
          const count = md[level];
          const pct = (count / totalDist) * 100;
          if (pct === 0) return null;
          return (
            <View key={level} style={[styles.barSegment, { flex: count }]}>
              <MasteryBadge level={level} />
              <Text style={styles.barCount}>{count}</Text>
            </View>
          );
        })}
      </View>

      {/* Recognition gap */}
      {data.recognition_only_count > 0 && (
        <View style={styles.gapBox}>
          <Text style={styles.gapTitle}>Recognition-Only Gap</Text>
          <Text style={styles.gapCount}>{data.recognition_only_count}</Text>
          <Text style={styles.gapSub}>
            Questions you chose correctly on MCQ but couldn't recall freely. Focus on these.
          </Text>
        </View>
      )}

      {/* Weakest systems */}
      {data.weakest_systems.length > 0 && (
        <>
          <Text style={styles.sectionLabel}>WEAKEST SYSTEMS</Text>
          {data.weakest_systems.map(sys => (
            <View key={sys.system_tag} style={styles.systemRow}>
              <Text style={styles.systemTag}>{sys.system_tag}</Text>
              <Text style={styles.systemScore}>avg {sys.avg_typed_score.toFixed(1)}/4</Text>
            </View>
          ))}
        </>
      )}

      {/* Weakest topics */}
      {data.weakest_topics.length > 0 && (
        <>
          <Text style={styles.sectionLabel}>WEAKEST TOPICS</Text>
          <View style={styles.topicRow}>
            {data.weakest_topics.map(t => (
              <View key={t} style={styles.topicChip}>
                <Text style={styles.topicText}>{t}</Text>
              </View>
            ))}
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: spacing.lg, paddingTop: spacing.xl },
  center: { flex: 1, backgroundColor: colors.bg, alignItems: 'center', justifyContent: 'center' },
  heading: { fontSize: font.xxl, fontWeight: '700', color: colors.textPrimary, marginBottom: spacing.lg },
  statRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.lg },
  statBox: {
    flex: 1, backgroundColor: colors.card, borderRadius: radius.md,
    padding: spacing.md, alignItems: 'center',
  },
  statValue: { fontSize: font.xl, fontWeight: '700', color: colors.textPrimary },
  statLabel: { fontSize: font.xs, color: colors.textSecondary, textAlign: 'center', marginTop: 4 },
  statSub: { fontSize: font.xs, color: colors.textMuted, marginTop: 2 },
  sectionLabel: {
    fontSize: font.xs, fontWeight: '700', color: colors.textMuted,
    letterSpacing: 1.2, marginBottom: spacing.sm, marginTop: spacing.md,
  },
  barContainer: {
    flexDirection: 'row', gap: spacing.xs,
    backgroundColor: colors.card, borderRadius: radius.md,
    padding: spacing.sm, marginBottom: spacing.md,
  },
  barSegment: { alignItems: 'center', gap: 4, paddingVertical: spacing.xs },
  barCount: { fontSize: font.sm, color: colors.textSecondary, fontWeight: '600' },
  gapBox: {
    backgroundColor: '#1A1000', borderLeftWidth: 3, borderLeftColor: colors.warning,
    borderRadius: radius.sm, padding: spacing.md, marginBottom: spacing.md,
  },
  gapTitle: { fontSize: font.sm, fontWeight: '700', color: colors.warning },
  gapCount: { fontSize: 36, fontWeight: '800', color: colors.warning },
  gapSub: { fontSize: font.xs, color: colors.textSecondary, marginTop: 4 },
  systemRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    backgroundColor: colors.card, borderRadius: radius.sm,
    padding: spacing.md, marginBottom: 4,
  },
  systemTag: { color: colors.textPrimary, fontSize: font.sm },
  systemScore: { color: colors.textSecondary, fontSize: font.sm },
  topicRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  topicChip: {
    backgroundColor: '#1D3461', borderRadius: radius.full,
    paddingVertical: spacing.xs, paddingHorizontal: spacing.sm,
  },
  topicText: { color: colors.primary, fontSize: font.xs },
});
