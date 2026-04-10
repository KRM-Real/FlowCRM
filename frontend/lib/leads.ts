import { apiFetch } from "@/lib/api-client";
import type {
  Lead,
  LeadFilters,
  LeadFormInput,
  PaginatedResponse,
} from "@/types/leads";

function toLeadPayload(values: LeadFormInput) {
  return {
    name: values.name.trim(),
    email: values.email.trim() || null,
    phone: values.phone.trim() || null,
    source: values.source,
    status: values.status,
    owner_id: values.owner_id || null,
  };
}

function buildLeadListPath(organizationId: number, filters: LeadFilters = {}) {
  const params = new URLSearchParams();

  if (filters.status) {
    params.set("status", filters.status);
  }
  if (filters.owner) {
    params.set("owner", filters.owner);
  }
  if (filters.search) {
    params.set("search", filters.search);
  }
  if (filters.page && filters.page > 1) {
    params.set("page", String(filters.page));
  }

  const query = params.toString();
  const basePath = `/api/organizations/${organizationId}/leads/`;
  return query ? `${basePath}?${query}` : basePath;
}

export async function listLeads(
  organizationId: number,
  filters: LeadFilters = {},
) {
  return apiFetch<PaginatedResponse<Lead>>(buildLeadListPath(organizationId, filters));
}

export async function createLead(organizationId: number, values: LeadFormInput) {
  return apiFetch<Lead>(`/api/organizations/${organizationId}/leads/`, {
    method: "POST",
    body: JSON.stringify(toLeadPayload(values)),
  });
}

export async function updateLead(
  organizationId: number,
  leadId: string,
  values: LeadFormInput,
) {
  return apiFetch<Lead>(`/api/organizations/${organizationId}/leads/${leadId}/`, {
    method: "PATCH",
    body: JSON.stringify(toLeadPayload(values)),
  });
}

export async function deleteLead(organizationId: number, leadId: string) {
  return apiFetch<null>(`/api/organizations/${organizationId}/leads/${leadId}/`, {
    method: "DELETE",
  });
}
