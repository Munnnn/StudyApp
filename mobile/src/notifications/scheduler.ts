/**
 * Local notification scheduler.
 * - Cancels all existing Pimp notifications then re-schedules a repeating one.
 * - Respects quiet hours by not scheduling when the current time is inside them.
 * - Notification tap deep-links to the Study tab via the navigation state.
 */
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

const NOTIFICATION_IDENTIFIER = 'pimp-study-reminder';

const BODIES = [
  'Pimp question ready',
  'Time for a rapid recall check',
  'Quick Step 1 question',
  'Your attending is waiting...',
  'One more before rounds?',
];

function randomBody(): string {
  return BODIES[Math.floor(Math.random() * BODIES.length)];
}

export async function requestPermissions(): Promise<boolean> {
  const { status } = await Notifications.requestPermissionsAsync();
  return status === 'granted';
}

export async function scheduleStudyReminders(
  intervalMinutes: number,
  quietStart?: string | null, // "HH:MM"
  quietEnd?: string | null    // "HH:MM"
): Promise<void> {
  // Cancel previous
  await cancelStudyReminders();

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('pimp-study', {
      name: 'Study Reminders',
      importance: Notifications.AndroidImportance.DEFAULT,
    });
  }

  // Skip scheduling if currently in quiet hours
  if (isInQuietHours(quietStart, quietEnd)) {
    return;
  }

  const intervalSeconds = intervalMinutes * 60;

  await Notifications.scheduleNotificationAsync({
    identifier: NOTIFICATION_IDENTIFIER,
    content: {
      title: 'Pimp',
      body: randomBody(),
      data: { deepLink: 'study' },
      sound: true,
    },
    trigger: {
      type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
      seconds: intervalSeconds,
      repeats: true,
    },
  });
}

export async function cancelStudyReminders(): Promise<void> {
  await Notifications.cancelScheduledNotificationAsync(NOTIFICATION_IDENTIFIER);
}

export function setupNotificationHandler(): void {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowBanner: true,
      shouldShowList: true,
      shouldPlaySound: false,
      shouldSetBadge: false,
    }),
  });
}

export function isInQuietHours(
  quietStart?: string | null,
  quietEnd?: string | null
): boolean {
  if (!quietStart || !quietEnd) return false;
  const now = new Date();
  const [sh, sm] = quietStart.split(':').map(Number);
  const [eh, em] = quietEnd.split(':').map(Number);
  const nowMin = now.getHours() * 60 + now.getMinutes();
  const startMin = sh * 60 + sm;
  const endMin = eh * 60 + em;
  if (startMin <= endMin) {
    return nowMin >= startMin && nowMin < endMin;
  }
  // Wraps midnight
  return nowMin >= startMin || nowMin < endMin;
}
