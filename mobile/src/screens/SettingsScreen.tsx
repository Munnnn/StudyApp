import React, { useState } from 'react';
import {
  Alert,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { updateUser } from '../api/endpoints';
import { useStore } from '../state/store';
import { scheduleStudyReminders, cancelStudyReminders } from '../notifications/scheduler';
import { Button } from '../components/Button';
import { colors, font, radius, spacing } from '../theme';

const INTERVALS = [10, 30, 60, 120];

export function SettingsScreen() {
  const { user, setUser } = useStore();
  const [saving, setSaving] = useState(false);
  const [interval, setInterval] = useState(user?.notification_interval_min ?? 30);
  const [paused, setPaused] = useState(user?.paused ?? false);
  const [quietStart, setQuietStart] = useState(user?.quiet_hours_start ?? '');
  const [quietEnd, setQuietEnd] = useState(user?.quiet_hours_end ?? '');

  async function save() {
    setSaving(true);
    try {
      const updated = await updateUser({
        notification_interval_min: interval,
        paused,
        quiet_hours_start: quietStart || null,
        quiet_hours_end: quietEnd || null,
      } as any);
      setUser(updated as any);

      if (paused) {
        await cancelStudyReminders();
      } else {
        await scheduleStudyReminders(interval, quietStart || null, quietEnd || null);
      }

      Alert.alert('Saved', 'Notification settings updated.');
    } catch (e: any) {
      Alert.alert('Error', e?.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      <Text style={styles.heading}>Settings</Text>

      {/* Pause toggle */}
      <View style={styles.row}>
        <View style={styles.rowBody}>
          <Text style={styles.rowLabel}>Pause all reminders</Text>
          <Text style={styles.rowSub}>No notifications until re-enabled</Text>
        </View>
        <Switch
          value={paused}
          onValueChange={setPaused}
          trackColor={{ true: colors.primary }}
          thumbColor={colors.white}
        />
      </View>

      {/* Interval selection */}
      <Text style={styles.sectionLabel}>STUDY INTERVAL</Text>
      <View style={styles.chipRow}>
        {INTERVALS.map(min => (
          <TouchableOpacity
            key={min}
            style={[styles.chip, interval === min && styles.chipActive]}
            onPress={() => setInterval(min)}
            disabled={paused}
          >
            <Text style={[styles.chipText, interval === min && styles.chipTextActive]}>
              {min < 60 ? `${min}m` : `${min / 60}h`}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Quiet hours */}
      <Text style={styles.sectionLabel}>QUIET HOURS</Text>
      <Text style={styles.sub}>No notifications between these times (HH:MM format)</Text>
      <View style={styles.timeRow}>
        <TextInput
          style={styles.timeInput}
          placeholder="Start (e.g. 22:00)"
          placeholderTextColor={colors.textMuted}
          value={quietStart}
          onChangeText={setQuietStart}
          keyboardType="numeric"
        />
        <Text style={styles.timeSep}>→</Text>
        <TextInput
          style={styles.timeInput}
          placeholder="End (e.g. 07:00)"
          placeholderTextColor={colors.textMuted}
          value={quietEnd}
          onChangeText={setQuietEnd}
          keyboardType="numeric"
        />
      </View>

      <Button title="Save settings" loading={saving} onPress={save} fullWidth style={styles.mt} />

      <View style={styles.divider} />
      <Text style={styles.info}>Device ID: {user?.device_id?.slice(0, 16) ?? '—'}…</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: spacing.lg, paddingTop: spacing.xl },
  heading: { fontSize: font.xxl, fontWeight: '700', color: colors.textPrimary, marginBottom: spacing.lg },
  sectionLabel: {
    fontSize: font.xs, fontWeight: '700', color: colors.textMuted,
    letterSpacing: 1.2, marginTop: spacing.lg, marginBottom: spacing.sm,
  },
  row: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: colors.card, borderRadius: radius.md,
    padding: spacing.md, marginBottom: spacing.sm,
  },
  rowBody: { flex: 1 },
  rowLabel: { fontSize: font.md, color: colors.textPrimary, fontWeight: '600' },
  rowSub: { fontSize: font.xs, color: colors.textSecondary, marginTop: 2 },
  chipRow: { flexDirection: 'row', gap: spacing.sm, flexWrap: 'wrap' },
  chip: {
    paddingVertical: spacing.sm, paddingHorizontal: spacing.md,
    backgroundColor: colors.card, borderRadius: radius.full,
    borderWidth: 1, borderColor: colors.border,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.textSecondary, fontWeight: '600', fontSize: font.sm },
  chipTextActive: { color: colors.white },
  sub: { fontSize: font.xs, color: colors.textSecondary, marginBottom: spacing.sm },
  timeRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  timeInput: {
    flex: 1, backgroundColor: colors.card, borderRadius: radius.md,
    color: colors.textPrimary, padding: spacing.md, fontSize: font.md,
  },
  timeSep: { color: colors.textSecondary, fontSize: font.lg },
  mt: { marginTop: spacing.lg },
  divider: { height: 1, backgroundColor: colors.border, marginVertical: spacing.xl },
  info: { fontSize: font.xs, color: colors.textMuted },
});
