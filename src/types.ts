export interface Indicator {
  id: string;
  name: string;
  value: string;
  unit: string;
  period: string;
  source: string;
  source_url: string;
  category: string;
  updated_at: string;
}

export interface Publication {
  id: string;
  title: string;
  date: string;
  source: string;
  url: string;
  type: string;
  description: string;
}
