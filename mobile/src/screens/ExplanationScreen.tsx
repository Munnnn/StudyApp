/**
 * Step 3: Explanation / teaching screen.
 * Receives the full explanation payload from MCQScreen.
 * Shows: typed answer | correct answer | mastery | explanation | wrong-answer analysis | takeaway | follow-up questions.
 */
import React, { useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { ExplanationResponse } from '../api/endpoints';
import { Button } from '../components/Button';
import { MasteryBadge } from '../components/MasteryBadge';
import { colors, font, radius, spacing } from '../theme';

const GAP_LABELS: Record<string, string> = {
  both: 'Strong understanding',
  recognition_only: 'Recognition only — you need more free recall practice on this',
  recall_only: 'Good recall but missed the MCQ — review answer choices',
  neither: 'Needs work — review this concept',
};

export function ExplanationScreen() {
  const { params } = useRoute<any>();
  const nav = useNavigation<any>();
  const e: ExplanationResponse = params.explanation;
  const [revealedFollowups, setRevealedFollowups] = useState<boolean[]>(
    e.follow_up_questions.map(() => false)
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      {/* Mastery badge */}
      <View style={styles.badgeRow}>
        <MasteryBadge level={e.mastery_level} />
        {e.recall_gap !== 'both' && (
          <Text style={styles.gapNote}>{GAP_LABELS[e.recall_gap]}</Text>
        )}
      </View>

      {/* Answer comparison */}
      <View style={styles.section}>
        <Text style={styles.sectionLabel}>YOUR ANSWER</Text>
        <View style={styles.answerBox}>
          <Text style={[styles.answerText, { color: e.typed_answer_score >= 3 ? colors.success : e.typed_answer_score >= 1 ? colors.warning : colors.danger }]}>
            {e.typed_answer_raw || '(blank)'}
          </Text>
          <Text style={styles.scoreText}>Score: {e.typed_answer_score}/4</Text>
        </View>

        <Text style={[styles.sectionLabel, styles.mt]}>CORRECT ANSWER</Text>
        <View style={[styles.answerBox, styles.correctBox]}>
          <Text style={[styles.answerText, { color: colors.success }]}>{e.correct_answer}</Text>
        </View>

        {/* MCQ result */}
        <View style={styles.mcqRow}>
          <Text style={styles.mcqLabel}>MCQ:</Text>
          <Text style={[styles.mcqResult, { color: e.mcq_correct ? colors.success : colors.danger }]}>
            {e.mcq_correct ? '✓ Correct' : '✗ Incorrect'}
          </Text>
        </View>
      </View>

      {/* Explanation */}
      <View style={styles.section}>
        <Text style={styles.sectionLabel}>EXPLANATION</Text>
        <Text style={styles.bodyText}>{e.step_by_step_explanation}</Text>
      </View>

      {/* Wrong answer analysis */}
      {e.wrong_answer_analysis.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>WHY OTHER OPTIONS ARE WRONG</Text>
          {e.wrong_answer_analysis.map((w, i) => (
            <View key={i} style={styles.wrongRow}>
              <Text style={styles.wrongBullet}>✗</Text>
              <Text style={styles.wrongText}>{w}</Text>
            </View>
          ))}
        </View>
      )}

      {/* High-yield takeaway */}
      <View style={styles.takeawayBox}>
        <Text style={styles.takeawayLabel}>HIGH-YIELD TAKEAWAY</Text>
        <Text style={styles.takeawayText}>{e.high_yield_takeaway}</Text>
      </View>

      {/* Follow-up pimp questions */}
      {e.follow_up_questions.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>FOLLOW-UP QUESTIONS</Text>
          {e.follow_up_questions.map((q, i) => (
            <View key={i} style={styles.followupBox}>
              <Text style={styles.followupQ}>{q}</Text>
              {!revealedFollowups[i] ? (
                <TouchableOpacity
                  onPress={() => {
                    const next = [...revealedFollowups];
                    next[i] = true;
                    setRevealedFollowups(next);
                  }}
                >
                  <Text style={styles.revealTap}>Tap to think, then reveal →</Text>
                </TouchableOpacity>
              ) : (
                <Text style={styles.followupHint}>Think through this using the explanation above.</Text>
              )}
            </View>
          ))}
        </View>
      )}

      <Button
        title="Next question"
        onPress={() => nav.replace('FreeRecall')}
        fullWidth
        style={styles.mt}
      />
      <View style={styles.bottomPad} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: spacing.lg, paddingTop: spacing.xl },
  badgeRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.lg },
  gapNote: { flex: 1, fontSize: font.xs, color: colors.textSecondary },
  section: { marginBottom: spacing.lg },
  sectionLabel: {
    fontSize: font.xs,
    fontWeight: '700',
    color: colors.textMuted,
    letterSpacing: 1.2,
    marginBottom: spacing.xs,
  },
  answerBox: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.xs,
  },
  correctBox: { borderWidth: 1, borderColor: colors.success + '44' },
  answerText: { fontSize: font.md, lineHeight: 22 },
  scoreText: { fontSize: font.xs, color: colors.textMuted, marginTop: 4 },
  mcqRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginTop: spacing.xs },
  mcqLabel: { fontSize: font.sm, color: colors.textSecondary },
  mcqResult: { fontSize: font.sm, fontWeight: '700' },
  bodyText: { fontSize: font.md, color: colors.textPrimary, lineHeight: 24 },
  wrongRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.sm },
  wrongBullet: { color: colors.danger, fontSize: font.sm, marginTop: 2 },
  wrongText: { flex: 1, fontSize: font.sm, color: colors.textSecondary, lineHeight: 20 },
  takeawayBox: {
    backgroundColor: '#0F2A1A',
    borderLeftWidth: 3,
    borderLeftColor: colors.success,
    borderRadius: radius.sm,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  takeawayLabel: {
    fontSize: font.xs,
    fontWeight: '700',
    color: colors.success,
    letterSpacing: 1.2,
    marginBottom: spacing.xs,
  },
  takeawayText: { fontSize: font.md, color: colors.textPrimary, fontWeight: '600', lineHeight: 22 },
  followupBox: { backgroundColor: colors.card, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.sm },
  followupQ: { fontSize: font.sm, color: colors.textPrimary, fontWeight: '600', marginBottom: spacing.xs },
  revealTap: { color: colors.primary, fontSize: font.sm },
  followupHint: { color: colors.textSecondary, fontSize: font.sm, fontStyle: 'italic' },
  mt: { marginTop: spacing.md },
  bottomPad: { height: spacing.xl },
});
