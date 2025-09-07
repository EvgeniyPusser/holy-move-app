import { useMovingStore } from '../stores/movingStore';
import { useMutation } from '@tanstack/react-query';
import { calculateMoving } from '../queries/movingApi';
import React from 'react';

export const MainPage: React.FC = () => {
  const { fromZip, toZip, rooms, moveDate, setForm, setResults } = useMovingStore();
  const mutation = useMutation({
    mutationFn: calculateMoving,
    onSuccess: (data) => setResults(data),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({ fromZip, toZip, rooms, moveDate });
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 400, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
      <input value={fromZip} onChange={e => setForm({ fromZip: e.target.value })} placeholder="From ZIP" required />
      <input value={toZip} onChange={e => setForm({ toZip: e.target.value })} placeholder="To ZIP" required />
      <input type="number" value={rooms} onChange={e => setForm({ rooms: Number(e.target.value) })} placeholder="Rooms" min={1} required />
      <input type="date" value={moveDate} onChange={e => setForm({ moveDate: e.target.value })} required />
      <button type="submit">Calculate</button>
      {mutation.isLoading && <div>Calculating...</div>}
      {mutation.isError && <div>Error: {mutation.error instanceof Error ? mutation.error.message : 'Unknown error'}</div>}
    </form>
  );
};
