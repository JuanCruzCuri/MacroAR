export interface Indicator {
  id: string;
  indicator_key: string;
  name: string;
  value: string;
  unit: string;
  period: string;
  source: string;
  source_url: string;
  category: string;
  updated_at: string | null;
}

export interface Publication {
  id: string;
  title: string;
  date: string | null;
  source: string;
  url: string;
  type: string;
  description: string;
}

export interface ScrapeStatus {
  last_scrape: string | null;
  next_scrape: string | null;
  timezone: string;
}
