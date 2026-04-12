import React from 'react';
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TouchableOpacity,
  TouchableOpacityProps,
  ViewStyle,
} from 'react-native';
import { colors, radius, spacing, font } from '../theme';

interface Props extends TouchableOpacityProps {
  title: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  loading?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
}

export function Button({ title, variant = 'primary', loading, fullWidth, style, disabled, ...rest }: Props) {
  const bg =
    variant === 'primary' ? colors.primary :
    variant === 'secondary' ? colors.surface :
    variant === 'danger' ? colors.danger :
    'transparent';
  const textColor = variant === 'ghost' ? colors.primary : colors.white;

  return (
    <TouchableOpacity
      style={[
        styles.base,
        { backgroundColor: bg },
        fullWidth && styles.fullWidth,
        (disabled || loading) && styles.disabled,
        style,
      ]}
      disabled={disabled || loading}
      activeOpacity={0.7}
      {...rest}
    >
      {loading ? (
        <ActivityIndicator color={textColor} />
      ) : (
        <Text style={[styles.label, { color: textColor }]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  fullWidth: { width: '100%' },
  disabled: { opacity: 0.5 },
  label: { fontSize: font.md, fontWeight: '600', letterSpacing: 0.3 },
});
