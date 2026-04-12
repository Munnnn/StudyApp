import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { AppNavigator } from './src/nav';

export default function App() {
  return (
    <>
      <StatusBar style="light" />
      <AppNavigator />
    </>
  );
}
