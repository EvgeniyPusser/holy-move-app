export const calculateMoving = async ({ fromZip, toZip, rooms, moveDate }: {
  fromZip: string;
  toZip: string;
  rooms: number;
  moveDate: string;
}) => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/api/calculate-moving`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fromZip, toZip, rooms, moveDate }),
  });
  return response.json();
};

export const getRoute = async ({ fromZip, toZip }: { fromZip: string; toZip: string }) => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/api/get-route?fromZip=${fromZip}&toZip=${toZip}`);
  return response.json();
};
