/**
 * Step 2: MCQ selection.
 * Receives shuffled options from the store (populated after typed submit).
 * On selection → POST /study/attempts/mcq → replace() to Explanation.
 */
import React, { useRef, useState } from 'react';
import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { submitMCQ } from '../api/endpoints';
import { useStore } from '../state/store';
import { Button } from '../components/Button';
import { QuestionCard } from '../components/QuestionCard';
import { colors, font, radius, spacing } from '../theme';

export function MCQScreen() {
  const nav = useNavigation<any>();
  const { currentAttempt, clearAttempt } = useStore();
  const [selected, setSelected] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const startRef = useRef(Date.now());

  if (!currentAttempt) return null;

  async function handleSubmit() {
    if (selected === null) return;
    setSubmitting(true);
    try {
      const elapsed = Date.now() - startRef.current;
      const explanation = await submitMCQ({
        attempt_id: currentAttempt!.attempt_id,
        mcq_selected_index: selected,
        response_time_ms: elapsed,
      });
      clearAttempt();
      nav.replace('Explanation', { explanation });
    } catch (e: any) {
      Alert.alert('Error', e?.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      <Text style={styles.label}>WHICH IS CORRECT?</Text>
      <QuestionCard question={currentAttempt.attending_question} />

      <View style={styles.options}>
        {currentAttempt.mcq_options.map((opt, idx) => (
          <TouchableOpacity
            key={idx}
            style={[styles.option, selected === idx && styles.optionSelected]}
            onPress={() => setSelected(idx)}
            activeOpacity={0.7}
          >
            <View style={[styles.optionCircle, selected === idx && styles.optionCircleSelected]}>
              <Text style={[styles.optionLetter, selected === idx && styles.optionLetterSelected]}>
                {String.fromCharCode(65 + idx)}
              </Text>
            </View>
            <Text style={[styles.optionText, selected === idx && styles.optionTextSelected]}>
              {opt}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Button
        title="Confirm selection"
        loading={submitting}
        disabled={selected === null}
        onPress={handleSubmit}
        fullWidth
        style={styles.mt}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: spacing.lg, paddingTop: spacing.xl },
  label: {
    fontSize: font.xs,
    fontWeight: '700',
    color: colors.textSecondary,
    letterSpacing: 1.2,
    marginBottom: spacing.sm,
  },
  options: { gap: spacing.sm },
  option: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  optionSelected: { borderColor: colors.primary, backgroundColor: '#0F2044' },
  optionCircle: {
    width: 32, height: 32,
    borderRadius: 16,
    backgroundColor: colors.surface,
    alignItems: 'center', justifyContent: 'center',
  },
  optionCircleSelected: { backgroundColor: colors.primary },
  optionLetter: { fontSize: font.sm, fontWeight: '700', color: colors.textSecondary },
  optionLetterSelected: { color: colors.white },
  optionText: { flex: 1, fontSize: font.md, color: colors.textPrimary, lineHeight: 22 },
  optionTextSelected: { color: colors.white },
  mt: { marginTop: spacing.lg },
});
