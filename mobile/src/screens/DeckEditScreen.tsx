import React, { useCallback, useState } from 'react';
import {
  Alert,
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';
import { deleteCard, getDeck, listCards, Card, Deck } from '../api/endpoints';
import { Button } from '../components/Button';
import { colors, font, radius, spacing } from '../theme';

export function DeckEditScreen() {
  const { params } = useRoute<any>();
  const nav = useNavigation<any>();
  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<Card[]>([]);

  useFocusEffect(useCallback(() => {
    getDeck(params.deckId).then(setDeck);
    listCards(params.deckId).then(setCards);
  }, [params.deckId]));

  const handleDeleteCard = (card: Card) => {
    Alert.alert('Delete card?', card.front, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete', style: 'destructive',
        onPress: async () => {
          await deleteCard(card.id);
          setCards(c => c.filter(x => x.id !== card.id));
        },
      },
    ]);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title} numberOfLines={1}>{deck?.title ?? '…'}</Text>
        <Text style={styles.meta}>{cards.length} cards</Text>
      </View>
      <FlatList
        data={cards}
        keyExtractor={c => c.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No cards yet.</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.cardBody}>
              <Text style={styles.front}>{item.front}</Text>
              <Text style={styles.back}>{item.back}</Text>
              {(item.system_tag || item.topic_tag) && (
                <Text style={styles.tag}>{[item.system_tag, item.topic_tag].filter(Boolean).join(' · ')}</Text>
              )}
            </View>
            <TouchableOpacity onPress={() => handleDeleteCard(item)}>
              <Text style={styles.del}>✕</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: { padding: spacing.lg, paddingTop: spacing.xl },
  title: { fontSize: font.xl, fontWeight: '700', color: colors.textPrimary },
  meta: { fontSize: font.sm, color: colors.textSecondary, marginTop: 4 },
  list: { paddingHorizontal: spacing.lg, paddingBottom: spacing.xl },
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  cardBody: { flex: 1 },
  front: { fontSize: font.sm, fontWeight: '600', color: colors.textPrimary },
  back: { fontSize: font.sm, color: colors.textSecondary, marginTop: 2 },
  tag: { fontSize: font.xs, color: colors.primary, marginTop: 4 },
  del: { fontSize: 18, color: colors.textMuted, paddingLeft: spacing.sm },
  empty: { color: colors.textSecondary, textAlign: 'center', marginTop: spacing.xl },
});
