export const LEAD_STATUSES = [
  "NEW",
  "CONTACTED",
  "QUALIFIED",
  "LOST",
  "WON",
] as const;

export const LEAD_SOURCES = [
  "MANUAL",
  "FACEBOOK",
  "WEBSITE",
  "REFERRAL",
] as const;

export type LeadStatus = (typeof LEAD_STATUSES)[number];
export type LeadSource = (typeof LEAD_SOURCES)[number];

export type Lead = {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  source: LeadSource;
  status: LeadStatus;
  owner_id: string | null;
  owner_email: string | null;
  owner_name: string | null;
  created_at: string;
  updated_at: string;
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type LeadFilters = {
  status?: LeadStatus | "";
  owner?: string;
  search?: string;
  page?: number;
};

export type LeadFormInput = {
  name: string;
  email: string;
  phone: string;
  source: LeadSource;
  status: LeadStatus;
  owner_id: string;
};
