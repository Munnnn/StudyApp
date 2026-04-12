/**
 * Step 1 of the study flow: free-recall.
 * Shows ONLY the attending question. No hints, no options.
 * On submit → POST /study/attempts/typed → navigates to MCQ (with replace).
 * replace() prevents back-navigation to this screen after seeing MCQ.
 */
import React, { useCallback, useRef, useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { getNextQuestion, submitTypedAnswer } from '../api/endpoints';
import { useStore } from '../state/store';
import { Button } from '../components/Button';
import { QuestionCard } from '../components/QuestionCard';
import { colors, font, spacing } from '../theme';

export function FreeRecallScreen() {
  const nav = useNavigation<any>();
  const { setCurrentAttempt } = useStore();

  const [question, setQuestion] = useState<any>(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [noCards, setNoCards] = useState(false);
  const startRef = useRef(Date.now());

  // Reload whenever the screen gains focus (e.g. switching tabs, coming back from explanation)
  useFocusEffect(useCallback(() => {
    loadNext();
  }, []));

  async function loadNext(force = false) {
    setLoading(true);
    setAnswer('');
    setNoCards(false);
    try {
      const q = await getNextQuestion(force);
      setQuestion(q);
      startRef.current = Date.now();
    } catch (e: any) {
      if (e?.status === 404) setNoCards(true);
      else Alert.alert('Error', e?.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit() {
    if (!answer.trim()) {
      Alert.alert('', 'Please type your answer before submitting.');
      return;
    }
    setSubmitting(true);
    try {
      const elapsed = Date.now() - startRef.current;
      const res = await submitTypedAnswer({
        generated_question_id: question.generated_question_id,
        typed_answer: answer.trim(),
        response_time_ms: elapsed,
      });
      setCurrentAttempt({
        attempt_id: res.attempt_id,
        generated_question_id: question.generated_question_id,
        attending_question: question.attending_question,
        mcq_options: res.mcq_options,
        typed_answer: answer.trim(),
      });
      // CRITICAL: replace() — no back navigation to this screen
      nav.replace('MCQ');
    } catch (e: any) {
      Alert.alert('Error', e?.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <Text style={styles.loading}>Loading question…</Text>
      </View>
    );
  }

  if (noCards) {
    return (
      <View style={styles.center}>
        <Text style={styles.noCards}>All caught up!</Text>
        <Text style={styles.noCardsSub}>No cards due right now. Add decks in the Decks tab, then come back here.</Text>
        <Button title="Check for Due Cards" onPress={loadNext} fullWidth style={styles.mt} />
        <Button
          title="Study Any Card (ignore schedule)"
          variant="secondary"
          onPress={() => loadNext(true)}
          fullWidth
          style={styles.mt}
        />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.label}>YOUR ATTENDING ASKS:</Text>
        <QuestionCard
          question={question?.attending_question}
          systemTag={question?.system_tag}
          topicTag={question?.topic_tag}
        />

        <Text style={styles.inputLabel}>Your answer:</Text>
        <TextInput
          style={styles.input}
          placeholder="Type from memory…"
          placeholderTextColor={colors.textMuted}
          value={answer}
          onChangeText={setAnswer}
          multiline
          autoFocus
          textAlignVertical="top"
        />

        <Button
          title="Submit answer"
          loading={submitting}
          onPress={handleSubmit}
          fullWidth
          style={styles.mt}
          disabled={!answer.trim()}
        />
      </ScrollView>
    </KeyboardAvoidingView>
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
  inputLabel: {
    fontSize: font.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  input: {
    backgroundColor: colors.card,
    borderRadius: 12,
    color: colors.textPrimary,
    fontSize: font.md,
    padding: spacing.md,
    minHeight: 120,
  },
  mt: { marginTop: spacing.md },
  center: {
    flex: 1,
    backgroundColor: colors.bg,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  loading: { color: colors.textSecondary, fontSize: font.md },
  noCards: { color: colors.textPrimary, fontSize: font.xl, fontWeight: '700' },
  noCardsSub: { color: colors.textSecondary, textAlign: 'center', marginTop: spacing.sm },
});
