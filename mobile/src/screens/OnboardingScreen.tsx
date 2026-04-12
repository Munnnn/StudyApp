import React, { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { getOrCreateDeviceId } from '../state/device';
import { useStore } from '../state/store';
import { ensureUser } from '../api/endpoints';
import { setupNotificationHandler, requestPermissions } from '../notifications/scheduler';
import { colors, font, spacing } from '../theme';

export function OnboardingScreen() {
  const [error, setError] = useState<string | null>(null);
  const { setDeviceId, setUser } = useStore();

  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      try {
        setupNotificationHandler();
        await requestPermissions();

        const id = await getOrCreateDeviceId();
        setDeviceId(id);

        const user = await ensureUser();
        if (!cancelled) setUser(user as any);
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? 'Failed to connect');
      }
    }
    bootstrap();
    return () => { cancelled = true; };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>Pimp</Text>
      <Text style={styles.subtitle}>USMLE Step 1 Micro-Quizzing</Text>
      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : (
        <ActivityIndicator color={colors.primary} style={styles.spinner} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  logo: {
    fontSize: 48,
    fontWeight: '800',
    color: colors.textPrimary,
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: font.md,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    marginBottom: spacing.xl,
  },
  spinner: { marginTop: spacing.xl },
  error: { color: colors.danger, textAlign: 'center', marginTop: spacing.lg },
});
