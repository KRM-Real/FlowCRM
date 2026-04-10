import { apiFetch } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/leads";
import type { OrganizationMember } from "@/types/organizations";

export async function listOrganizationMembers(organizationId: number) {
  return apiFetch<PaginatedResponse<OrganizationMember>>(
    `/api/organizations/${organizationId}/members/`,
  );
}
