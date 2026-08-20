const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface GeoPoint {
  latitude: number;
  longitude: number;
}

export interface ServiceProvider {
  provider_id: string;
  name: string;
  service_types: string[];
  location: GeoPoint;
  address: { formatted_address?: string };
  contact: { phone_primary?: string };
  distance_km: number;
  eta_minutes: number;
  rating?: number;
  availability_status: string;
  recommendation_score: number;
  recommendation_reason: string;
}

export interface GuidanceStep {
  step_number: number;
  title: str;
  instruction: str;
  caution?: string;
  is_critical: boolean;
}

export interface EmergencyResponse {
  incident: {
    category: string;
    severity: string;
    description_summary: string;
    is_life_threatening: boolean;
  };
  guidance: {
    summary: string;
    immediate_do_not_do: string[];
    steps: GuidanceStep[];
  };
  services: ServiceProvider[];
  recommended_actions: {
    action_id: string;
    action_type: string;
    label: string;
    target_contact?: string;
  }[];
  limitations?: string[];
}

export async function requestApi<T>(endpoint: string, method: string = 'GET', body?: any): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  const token = localStorage.getItem('raahat_auth_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error?.message || 'API request failed');
  }

  return json.data as T;
}
