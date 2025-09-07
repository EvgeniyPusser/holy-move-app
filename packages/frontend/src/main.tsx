import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from './components/App';
import 'leaflet/dist/leaflet.css';

const queryClient = new QueryClient();
const container = document.getElementById('root');
if (container) {
  createRoot(container).render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
}
