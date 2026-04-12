import React, { useState } from 'react';
import {
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import { useNavigation } from '@react-navigation/native';
import { addCard, createDeck } from '../api/endpoints';
import { useStore } from '../state/store';
import { Button } from '../components/Button';
import { colors, font, radius, spacing } from '../theme';

type Tab = 'csv' | 'manual';

interface ParsedRow { front: string; back: string; system_tag?: string; topic_tag?: string }

function parseCSVPreview(text: string): ParsedRow[] {
  const lines = text.split('\n').filter(Boolean);
  if (lines.length < 2) return [];
  const delim = lines[0].includes('\t') ? '\t' : ',';
  const headers = lines[0].split(delim).map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
  const fi = headers.indexOf('front');
  const bi = headers.indexOf('back');
  if (fi < 0 || bi < 0) return [];
  const si = headers.indexOf('system_tag') >= 0 ? headers.indexOf('system_tag') : headers.indexOf('system');
  const ti = headers.indexOf('topic_tag') >= 0 ? headers.indexOf('topic_tag') : headers.indexOf('topic');
  return lines.slice(1).slice(0, 10).map(line => {
    const cols = line.split(delim).map(c => c.trim().replace(/^["']|["']$/g, ''));
    return { front: cols[fi] ?? '', back: cols[bi] ?? '', system_tag: si >= 0 ? cols[si] : undefined, topic_tag: ti >= 0 ? cols[ti] : undefined };
  }).filter(r => r.front && r.back);
}

export function DeckUploadScreen() {
  const nav = useNavigation<any>();
  const [tab, setTab] = useState<Tab>('csv');
  const [deckTitle, setDeckTitle] = useState('');
  const [loading, setLoading] = useState(false);

  // CSV state
  const [csvText, setCsvText] = useState<string | null>(null);
  const [preview, setPreview] = useState<ParsedRow[]>([]);
  const [csvFilename, setCsvFilename] = useState('');

  // Manual state
  const [manualDeckId, setManualDeckId] = useState<string | null>(null);
  const [front, setFront] = useState('');
  const [back, setBack] = useState('');
  const [systemTag, setSystemTag] = useState('');
  const [topicTag, setTopicTag] = useState('');

  const pickCSV = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: ['text/csv', 'text/plain', 'text/tab-separated-values'] });
    if (result.canceled || !result.assets?.[0]) return;
    const asset = result.assets[0];
    setCsvFilename(asset.name);
    const text = await FileSystem.readAsStringAsync(asset.uri);
    setCsvText(text);
    setPreview(parseCSVPreview(text));
  };

  const importCSV = async () => {
    if (!deckTitle.trim() || !csvText) {
      Alert.alert('Required', 'Enter a deck title and pick a CSV file.');
      return;
    }
    setLoading(true);
    try {
      const deck = await createDeck({ title: deckTitle });
      const blob = new Blob([csvText], { type: 'text/csv' });
      const formData = new FormData();
      formData.append('file', blob as any, csvFilename || 'deck.csv');
      const deviceId = useStore.getState().deviceId;
      const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
      await fetch(`${BASE_URL}/api/v1/decks/${deck.id}/import-csv`, {
        method: 'POST',
        headers: { 'X-Device-Id': deviceId ?? '', 'Bypass-Tunnel-Reminder': 'true' },
        body: formData,
      });
      nav.goBack();
    } catch (e: any) {
      Alert.alert('Import failed', e?.message);
    } finally {
      setLoading(false);
    }
  };

  const addManualCard = async () => {
    if (!deckTitle.trim()) {
      Alert.alert('Required', 'Enter a deck title first.');
      return;
    }
    if (!front.trim() || !back.trim()) {
      Alert.alert('Required', 'Front and back are required.');
      return;
    }
    setLoading(true);
    try {
      // Create deck on first card
      let deckId = manualDeckId;
      if (!deckId) {
        const deck = await createDeck({ title: deckTitle });
        deckId = deck.id;
        setManualDeckId(deckId);
      }
      await addCard(deckId, {
        front: front.trim(),
        back: back.trim(),
        system_tag: systemTag.trim() || null,
        topic_tag: topicTag.trim() || null,
        difficulty: 2,
      });
      setFront(''); setBack(''); setSystemTag(''); setTopicTag('');
      Alert.alert('Added', 'Card added. Add another or go back.');
    } catch (e: any) {
      Alert.alert('Error', e?.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.heading}>New Deck</Text>
        <TextInput
          style={styles.input}
          placeholder="Deck title (e.g. Step 1 – Cardio)"
          placeholderTextColor={colors.textMuted}
          value={deckTitle}
          onChangeText={setDeckTitle}
        />

        {/* Tab toggle */}
        <View style={styles.tabs}>
          {(['csv', 'manual'] as Tab[]).map(t => (
            <TouchableOpacity
              key={t}
              style={[styles.tabBtn, tab === t && styles.tabActive]}
              onPress={() => setTab(t)}
            >
              <Text style={[styles.tabLabel, tab === t && styles.tabLabelActive]}>
                {t === 'csv' ? 'Upload CSV' : 'Add manually'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {tab === 'csv' ? (
          <View>
            <Button title="Pick CSV file" variant="secondary" onPress={pickCSV} fullWidth style={styles.mt} />
            {csvFilename ? <Text style={styles.filename}>{csvFilename}</Text> : null}
            {preview.length > 0 && (
              <>
                <Text style={styles.previewLabel}>Preview ({preview.length} rows shown)</Text>
                {preview.map((row, i) => (
                  <View key={i} style={styles.previewRow}>
                    <Text style={styles.previewFront}>{row.front}</Text>
                    <Text style={styles.previewBack}>{row.back}</Text>
                  </View>
                ))}
                <Button title="Import deck" loading={loading} onPress={importCSV} fullWidth style={styles.mt} />
              </>
            )}
          </View>
        ) : (
          <View style={styles.mt}>
            <TextInput style={[styles.input, styles.multiline]} placeholder="Front (question)" placeholderTextColor={colors.textMuted} value={front} onChangeText={setFront} multiline />
            <TextInput style={[styles.input, styles.multiline]} placeholder="Back (answer)" placeholderTextColor={colors.textMuted} value={back} onChangeText={setBack} multiline />
            <TextInput style={styles.input} placeholder="System tag (optional)" placeholderTextColor={colors.textMuted} value={systemTag} onChangeText={setSystemTag} />
            <TextInput style={styles.input} placeholder="Topic tag (optional)" placeholderTextColor={colors.textMuted} value={topicTag} onChangeText={setTopicTag} />
            <Button title="Add card" loading={loading} onPress={addManualCard} fullWidth style={styles.mt} />
          </View>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: spacing.lg, paddingTop: spacing.xl },
  heading: { fontSize: font.xxl, fontWeight: '700', color: colors.textPrimary, marginBottom: spacing.md },
  input: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    color: colors.textPrimary,
    padding: spacing.md,
    fontSize: font.md,
    marginBottom: spacing.sm,
  },
  multiline: { minHeight: 80, textAlignVertical: 'top' },
  tabs: { flexDirection: 'row', backgroundColor: colors.surface, borderRadius: radius.md, padding: 4, marginVertical: spacing.md },
  tabBtn: { flex: 1, paddingVertical: spacing.sm, borderRadius: radius.sm, alignItems: 'center' },
  tabActive: { backgroundColor: colors.card },
  tabLabel: { color: colors.textMuted, fontWeight: '600', fontSize: font.sm },
  tabLabelActive: { color: colors.textPrimary },
  mt: { marginTop: spacing.sm },
  filename: { color: colors.textSecondary, fontSize: font.sm, marginTop: spacing.xs },
  previewLabel: { color: colors.textSecondary, fontSize: font.sm, marginTop: spacing.md, marginBottom: spacing.xs },
  previewRow: { backgroundColor: colors.card, borderRadius: radius.sm, padding: spacing.sm, marginBottom: 4 },
  previewFront: { color: colors.textPrimary, fontSize: font.sm, fontWeight: '600' },
  previewBack: { color: colors.textSecondary, fontSize: font.sm },
});
