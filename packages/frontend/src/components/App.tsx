import React from 'react';
import { MainPage } from '../pages/MainPage';
import { ResultPage } from '../pages/ResultPage';
import { useMovingStore } from '../stores/movingStore';

export const App: React.FC = () => {
  const { results } = useMovingStore();
  return results ? <ResultPage /> : <MainPage />;
};
