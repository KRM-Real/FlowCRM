"use client";

import Link from "next/link";
import {
  startTransition,
  useDeferredValue,
  useEffect,
  useState,
  type FormEvent,
} from "react";

import { ApiError } from "@/lib/api-client";
import { getCurrentUser, logout } from "@/lib/auth";
import { createLead, deleteLead, listLeads, updateLead } from "@/lib/leads";
import { listOrganizationMembers } from "@/lib/organizations";
import type { AuthUser, MembershipSummary } from "@/types/auth";
import {
  LEAD_SOURCES,
  LEAD_STATUSES,
  type Lead,
  type LeadFormInput,
  type LeadStatus,
} from "@/types/leads";
import type { OrganizationMember } from "@/types/organizations";

const EMPTY_LEAD_FORM: LeadFormInput = {
  name: "",
  email: "",
  phone: "",
  source: "MANUAL",
  status: "NEW",
  owner_id: "",
};

function getDisplayName(member: OrganizationMember) {
  return member.user_email;
}

function isManagerOrAdmin(membership: MembershipSummary | undefined) {
  return membership?.role === "admin" || membership?.role === "manager";
}

export default function LeadsPageClient() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const [selectedOrganizationId, setSelectedOrganizationId] = useState<number | null>(
    null,
  );
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [resultCount, setResultCount] = useState(0);
  const [isLeadsLoading, setIsLeadsLoading] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<LeadStatus | "">("");
  const [ownerFilter, setOwnerFilter] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const deferredSearch = useDeferredValue(searchInput);

  const [formMode, setFormMode] = useState<"create" | "edit" | null>(null);
  const [editingLeadId, setEditingLeadId] = useState<string | null>(null);
  const [formValues, setFormValues] = useState<LeadFormInput>(EMPTY_LEAD_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Lead | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      try {
        const currentUser = await getCurrentUser();
        if (!isMounted) {
          return;
        }

        setUser(currentUser);
        setSelectedOrganizationId(
          currentUser.memberships.length > 0
            ? currentUser.memberships[0].organization_id
            : null,
        );
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setAuthError(
          error instanceof ApiError ? error.message : "Unable to load account.",
        );
      } finally {
        if (isMounted) {
          setIsPageLoading(false);
        }
      }
    }

    void loadUser();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedOrganizationId) {
      setMembers([]);
      setLeads([]);
      setResultCount(0);
      return;
    }

    const organizationId = selectedOrganizationId;
    let isMounted = true;

    async function loadMembers() {
      try {
        const response = await listOrganizationMembers(organizationId);
        if (!isMounted) {
          return;
        }

        setMembers(response.results);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setPageError(
          error instanceof ApiError
            ? error.message
            : "Unable to load organization members.",
        );
      }
    }

    void loadMembers();

    return () => {
      isMounted = false;
    };
  }, [selectedOrganizationId]);

  useEffect(() => {
    if (!selectedOrganizationId) {
      return;
    }

    const organizationId = selectedOrganizationId;
    let isMounted = true;

    async function loadLeads() {
      setIsLeadsLoading(true);
      setPageError(null);

      try {
        const response = await listLeads(organizationId, {
          status: statusFilter,
          owner: ownerFilter,
          search: deferredSearch.trim(),
        });

        if (!isMounted) {
          return;
        }

        setLeads(response.results);
        setResultCount(response.count);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setPageError(
          error instanceof ApiError ? error.message : "Unable to load leads.",
        );
      } finally {
        if (isMounted) {
          setIsLeadsLoading(false);
        }
      }
    }

    void loadLeads();

    return () => {
      isMounted = false;
    };
  }, [deferredSearch, ownerFilter, selectedOrganizationId, statusFilter]);

  const activeMembership = user?.memberships.find(
    (membership) => membership.organization_id === selectedOrganizationId,
  );
  const canManageLeads = isManagerOrAdmin(activeMembership);

  async function refreshLeads() {
    if (!selectedOrganizationId) {
      return;
    }

    const organizationId = selectedOrganizationId;
    setIsLeadsLoading(true);
    setPageError(null);

    try {
      const response = await listLeads(organizationId, {
        status: statusFilter,
        owner: ownerFilter,
        search: deferredSearch.trim(),
      });
      setLeads(response.results);
      setResultCount(response.count);
    } catch (error) {
      setPageError(error instanceof ApiError ? error.message : "Unable to load leads.");
    } finally {
      setIsLeadsLoading(false);
    }
  }

  function openCreateModal() {
    setFormMode("create");
    setEditingLeadId(null);
    setFormValues(EMPTY_LEAD_FORM);
    setFormError(null);
  }

  function openEditModal(lead: Lead) {
    setFormMode("edit");
    setEditingLeadId(lead.id);
    setFormValues({
      name: lead.name,
      email: lead.email ?? "",
      phone: lead.phone ?? "",
      source: lead.source,
      status: lead.status,
      owner_id: lead.owner_id ?? "",
    });
    setFormError(null);
  }

  function closeFormModal() {
    setFormMode(null);
    setEditingLeadId(null);
    setFormValues(EMPTY_LEAD_FORM);
    setFormError(null);
  }

  function onOrganizationChange(value: string) {
    startTransition(() => {
      const nextOrgId = Number(value);
      setSelectedOrganizationId(Number.isNaN(nextOrgId) ? null : nextOrgId);
      setOwnerFilter("");
      setSearchInput("");
      setStatusFilter("");
      closeFormModal();
      setDeleteTarget(null);
    });
  }

  function validateForm(values: LeadFormInput) {
    if (!values.name.trim()) {
      return "Lead name is required.";
    }
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedOrganizationId) {
      setFormError("Select an organization first.");
      return;
    }

    const organizationId = selectedOrganizationId;
    const validationMessage = validateForm(formValues);
    if (validationMessage) {
      setFormError(validationMessage);
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      if (formMode === "edit" && editingLeadId) {
        await updateLead(organizationId, editingLeadId, formValues);
      } else {
        await createLead(organizationId, formValues);
      }

      closeFormModal();
      await refreshLeads();
    } catch (error) {
      setFormError(error instanceof ApiError ? error.message : "Unable to save lead.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function confirmDelete() {
    if (!selectedOrganizationId || !deleteTarget) {
      return;
    }

    const organizationId = selectedOrganizationId;
    setIsDeleting(true);
    try {
      await deleteLead(organizationId, deleteTarget.id);
      setDeleteTarget(null);
      await refreshLeads();
    } catch (error) {
      setPageError(error instanceof ApiError ? error.message : "Unable to delete lead.");
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await logout();
    } finally {
      window.location.assign("/login");
    }
  }

  if (isPageLoading) {
    return (
      <main className="dashboard-page">
        <section className="dashboard-shell">
          <p className="dashboard-muted">Loading your workspace...</p>
        </section>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="dashboard-page">
        <section className="dashboard-shell">
          <p className="form-error">{authError ?? "Authentication required."}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="dashboard-page">
      <section className="dashboard-shell dashboard-shell--wide">
        <div className="dashboard-hero">
          <div>
            <p className="eyebrow">Lead Workspace</p>
            <h1>Leads</h1>
            <p className="dashboard-muted">
              Manage lead intake, ownership, and qualification from one place.
            </p>
          </div>

          <div className="dashboard-actions">
            <Link className="secondary-button" href="/dashboard">
              Back to dashboard
            </Link>
            <button
              className="secondary-button"
              disabled={isLoggingOut}
              onClick={handleLogout}
              type="button"
            >
              {isLoggingOut ? "Signing out..." : "Logout"}
            </button>
          </div>
        </div>

        <section className="dashboard-card">
          <div className="leads-toolbar">
            <div>
              <h2>Pipeline intake</h2>
              <p className="dashboard-muted">
                {resultCount} {resultCount === 1 ? "lead" : "leads"} in the current view.
              </p>
            </div>

            {canManageLeads ? (
              <button className="primary-button" onClick={openCreateModal} type="button">
                Create lead
              </button>
            ) : (
              <p className="dashboard-muted">
                Your role can view leads but cannot create or edit them.
              </p>
            )}
          </div>

          <div className="leads-filters">
            <label>
              <span>Organization</span>
              <select
                aria-label="Organization"
                onChange={(event) => onOrganizationChange(event.target.value)}
                value={selectedOrganizationId ?? ""}
              >
                {user.memberships.map((membership) => (
                  <option key={membership.id} value={membership.organization_id}>
                    {membership.organization_name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Status</span>
              <select
                aria-label="Status filter"
                onChange={(event) =>
                  setStatusFilter(event.target.value as LeadStatus | "")
                }
                value={statusFilter}
              >
                <option value="">All statuses</option>
                {LEAD_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Owner</span>
              <select
                aria-label="Owner filter"
                onChange={(event) => setOwnerFilter(event.target.value)}
                value={ownerFilter}
              >
                <option value="">All owners</option>
                {members.map((member) => (
                  <option key={member.id} value={member.user_id}>
                    {getDisplayName(member)}
                  </option>
                ))}
              </select>
            </label>

            <label className="leads-search">
              <span>Search</span>
              <input
                aria-label="Search leads"
                onChange={(event) => setSearchInput(event.target.value)}
                placeholder="Search by name or email"
                type="search"
                value={searchInput}
              />
            </label>
          </div>

          {pageError ? <p className="form-error">{pageError}</p> : null}

          {isLeadsLoading ? (
            <p className="dashboard-muted">Loading leads...</p>
          ) : leads.length === 0 ? (
            <div className="leads-empty">
              <p className="dashboard-muted">
                No leads match this view yet. Create one to start your pipeline.
              </p>
            </div>
          ) : (
            <div className="leads-table-wrap">
              <table className="leads-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Source</th>
                    <th>Status</th>
                    <th>Owner</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead) => (
                    <tr key={lead.id}>
                      <td>{lead.name}</td>
                      <td>{lead.email ?? "—"}</td>
                      <td>{lead.phone ?? "—"}</td>
                      <td>{lead.source}</td>
                      <td>
                        <span className={`status-pill status-pill--${lead.status.toLowerCase()}`}>
                          {lead.status}
                        </span>
                      </td>
                      <td>{lead.owner_name ?? lead.owner_email ?? "Unassigned"}</td>
                      <td>{new Date(lead.created_at).toLocaleDateString()}</td>
                      <td>
                        <div className="table-actions">
                          <button
                            className="secondary-button table-button"
                            disabled={!canManageLeads}
                            onClick={() => openEditModal(lead)}
                            type="button"
                          >
                            Edit
                          </button>
                          <button
                            className="secondary-button table-button table-button--danger"
                            disabled={!canManageLeads}
                            onClick={() => setDeleteTarget(lead)}
                            type="button"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {formMode ? (
          <div className="modal-backdrop" role="presentation">
            <section
              aria-label={formMode === "edit" ? "Edit lead" : "Create lead"}
              className="modal-panel"
            >
              <div className="modal-header">
                <div>
                  <p className="eyebrow">{formMode === "edit" ? "Update" : "Create"}</p>
                  <h2>{formMode === "edit" ? "Edit lead" : "Create lead"}</h2>
                </div>
                <button className="secondary-button" onClick={closeFormModal} type="button">
                  Close
                </button>
              </div>

              <form className="lead-form" onSubmit={handleSubmit}>
                <label>
                  <span>Name</span>
                  <input
                    aria-label="Lead name"
                    onChange={(event) =>
                      setFormValues((current) => ({
                        ...current,
                        name: event.target.value,
                      }))
                    }
                    type="text"
                    value={formValues.name}
                  />
                </label>

                <label>
                  <span>Email</span>
                  <input
                    aria-label="Lead email"
                    onChange={(event) =>
                      setFormValues((current) => ({
                        ...current,
                        email: event.target.value,
                      }))
                    }
                    type="email"
                    value={formValues.email}
                  />
                </label>

                <label>
                  <span>Phone</span>
                  <input
                    aria-label="Lead phone"
                    onChange={(event) =>
                      setFormValues((current) => ({
                        ...current,
                        phone: event.target.value,
                      }))
                    }
                    type="text"
                    value={formValues.phone}
                  />
                </label>

                <label>
                  <span>Source</span>
                  <select
                    aria-label="Lead source"
                    onChange={(event) =>
                      setFormValues((current) => ({
                        ...current,
                        source: event.target.value as LeadFormInput["source"],
                      }))
                    }
                    value={formValues.source}
                  >
                    {LEAD_SOURCES.map((source) => (
                      <option key={source} value={source}>
                        {source}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  <span>Status</span>
                  <select
                    aria-label="Lead status"
                    onChange={(event) =>
                      setFormValues((current) => ({
                        ...current,
                        status: event.target.value as LeadFormInput["status"],
                      }))
                    }
                    value={formValues.status}
                  >
                    {LEAD_STATUSES.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  <span>Owner</span>
                  <select
                    aria-label="Lead owner"
                    onChange={(event) =>
                      setFormValues((current) => ({
                        ...current,
                        owner_id: event.target.value,
                      }))
                    }
                    value={formValues.owner_id}
                  >
                    <option value="">Unassigned</option>
                    {members.map((member) => (
                      <option key={member.id} value={member.user_id}>
                        {getDisplayName(member)}
                      </option>
                    ))}
                  </select>
                </label>

                {formError ? <p className="form-error">{formError}</p> : null}

                <button className="primary-button" disabled={isSubmitting} type="submit">
                  {isSubmitting
                    ? "Saving..."
                    : formMode === "edit"
                      ? "Save changes"
                      : "Create lead"}
                </button>
              </form>
            </section>
          </div>
        ) : null}

        {deleteTarget ? (
          <div className="modal-backdrop" role="presentation">
            <section aria-label="Delete lead" className="modal-panel modal-panel--compact">
              <div className="modal-header">
                <div>
                  <p className="eyebrow">Remove</p>
                  <h2>Delete lead</h2>
                </div>
              </div>

              <p className="dashboard-muted">
                Delete <strong>{deleteTarget.name}</strong>? This action cannot be undone.
              </p>

              <div className="modal-actions">
                <button
                  className="secondary-button"
                  onClick={() => setDeleteTarget(null)}
                  type="button"
                >
                  Cancel
                </button>
                <button
                  className="primary-button danger-button"
                  disabled={isDeleting}
                  onClick={confirmDelete}
                  type="button"
                >
                  {isDeleting ? "Deleting..." : "Delete lead"}
                </button>
              </div>
            </section>
          </div>
        ) : null}
      </section>
    </main>
  );
}
