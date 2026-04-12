import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { deleteDeck, listDecks, Deck } from '../api/endpoints';
import { Button } from '../components/Button';
import { colors, font, radius, spacing } from '../theme';

export function DeckLibraryScreen() {
  const nav = useNavigation<any>();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setDecks(await listDecks());
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const handleDelete = (deck: Deck) => {
    Alert.alert('Delete deck', `Delete "${deck.title}" and all its cards?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          await deleteDeck(deck.id);
          load();
        },
      },
    ]);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Decks</Text>
        <Button title="+ New" onPress={() => nav.navigate('DeckUpload')} />
      </View>

      {loading ? (
        <ActivityIndicator color={colors.primary} style={styles.center} />
      ) : decks.length === 0 ? (
        <View style={styles.center}>
          <Text style={styles.empty}>No decks yet.</Text>
          <Text style={styles.emptySub}>Upload a CSV or create cards manually.</Text>
        </View>
      ) : (
        <FlatList
          data={decks}
          keyExtractor={(d) => d.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.card}
              onPress={() => nav.navigate('DeckEdit', { deckId: item.id })}
              onLongPress={() => handleDelete(item)}
            >
              <View style={styles.cardBody}>
                <Text style={styles.deckTitle}>{item.title}</Text>
                <Text style={styles.deckMeta}>{item.card_count} cards · {item.source_type}</Text>
              </View>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.lg,
    paddingTop: spacing.xl,
  },
  title: { fontSize: font.xxl, fontWeight: '700', color: colors.textPrimary },
  list: { paddingHorizontal: spacing.lg, paddingBottom: spacing.xl },
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
  },
  cardBody: { flex: 1 },
  deckTitle: { fontSize: font.md, fontWeight: '600', color: colors.textPrimary },
  deckMeta: { fontSize: font.sm, color: colors.textSecondary, marginTop: 4 },
  chevron: { fontSize: 24, color: colors.textMuted },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xl },
  empty: { fontSize: font.lg, color: colors.textSecondary, fontWeight: '600' },
  emptySub: { fontSize: font.sm, color: colors.textMuted, marginTop: spacing.xs, textAlign: 'center' },
});
