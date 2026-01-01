import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000/api'; // Update with your backend URL

export function useAmbulanceTracking(emergencyId) {
  return useQuery({
    queryKey: ['ambulance', emergencyId],
    queryFn: async () => {
      if (!emergencyId) return null;
      
      const response = await fetch(`${API_BASE_URL}/ambulance/${emergencyId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch ambulance data');
      }
      return response.json();
    },
    enabled: !!emergencyId, // Only run query if emergencyId exists
    refetchInterval: 5000, // Update every 5 seconds for real-time tracking
    staleTime: 0, // Always fetch fresh data
  });
}

export function useSelectedHospital(emergencyId) {
  return useQuery({
    queryKey: ['selectedHospital', emergencyId],
    queryFn: async () => {
      if (!emergencyId) return null;
      
      const response = await fetch(`${API_BASE_URL}/hospitals/${emergencyId}/selected`);
      if (!response.ok) {
        throw new Error('Failed to fetch hospital data');
      }
      return response.json();
    },
    enabled: !!emergencyId, // Only run query if emergencyId exists
    staleTime: 30000, // Hospital data doesn't change as frequently
  });
}
