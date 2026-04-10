import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { AnchorHTMLAttributes } from "react";

import LeadsPageClient from "@/app/dashboard/leads/leads-page-client";
import * as authApi from "@/lib/auth";
import * as leadsApi from "@/lib/leads";
import * as organizationsApi from "@/lib/organizations";
import type { AuthUser } from "@/types/auth";
import type { Lead } from "@/types/leads";

jest.mock("next/link", () => {
  return function MockLink({
    children,
    href,
    ...props
  }: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  };
});

jest.mock("@/lib/auth", () => ({
  getCurrentUser: jest.fn(),
  logout: jest.fn(),
}));

jest.mock("@/lib/leads", () => ({
  createLead: jest.fn(),
  deleteLead: jest.fn(),
  listLeads: jest.fn(),
  updateLead: jest.fn(),
}));

jest.mock("@/lib/organizations", () => ({
  listOrganizationMembers: jest.fn(),
}));

const mockUser: AuthUser = {
  id: "user-1",
  email: "admin@example.com",
  username: "admin",
  first_name: "Ava",
  last_name: "Stone",
  is_active: true,
  memberships: [
    {
      id: 1,
      organization_id: 3,
      organization_name: "Acme",
      organization_slug: "acme",
      role: "admin",
    },
    {
      id: 2,
      organization_id: 7,
      organization_name: "Beta",
      organization_slug: "beta",
      role: "manager",
    },
  ],
};

const mockLead: Lead = {
  id: "lead-1",
  name: "Qualified Prospect",
  email: "prospect@example.com",
  phone: "555-0100",
  source: "MANUAL",
  status: "QUALIFIED",
  owner_id: "rep-1",
  owner_email: "rep@example.com",
  owner_name: "rep@example.com",
  created_at: "2026-04-10T00:00:00Z",
  updated_at: "2026-04-10T00:00:00Z",
};

describe("LeadsPageClient", () => {
  beforeEach(() => {
    jest.mocked(authApi.getCurrentUser).mockResolvedValue(mockUser);
    jest.mocked(authApi.logout).mockResolvedValue(null);
    jest.mocked(organizationsApi.listOrganizationMembers).mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          user_id: "rep-1",
          user_email: "rep@example.com",
          organization_id: 3,
          role: "rep",
          created_at: "2026-04-10T00:00:00Z",
          updated_at: "2026-04-10T00:00:00Z",
        },
        {
          id: 2,
          user_id: "manager-1",
          user_email: "manager@example.com",
          organization_id: 3,
          role: "manager",
          created_at: "2026-04-10T00:00:00Z",
          updated_at: "2026-04-10T00:00:00Z",
        },
      ],
    });
    jest.mocked(leadsApi.listLeads).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [mockLead],
    });
    jest.mocked(leadsApi.createLead).mockResolvedValue(mockLead);
    jest.mocked(leadsApi.updateLead).mockResolvedValue(mockLead);
    jest.mocked(leadsApi.deleteLead).mockResolvedValue(null);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders lead rows after loading user, members, and leads", async () => {
    render(<LeadsPageClient />);

    expect(await screen.findByText("Qualified Prospect")).toBeInTheDocument();
    expect(screen.getAllByText("rep@example.com").length).toBeGreaterThan(0);
    expect(leadsApi.listLeads).toHaveBeenCalledWith(3, {
      owner: "",
      search: "",
      status: "",
    });
  });

  it("auto-selects the first organization and lets the user switch organizations", async () => {
    const user = userEvent.setup();
    render(<LeadsPageClient />);

    const organizationSelect = await screen.findByLabelText("Organization");
    expect(organizationSelect).toHaveValue("3");

    await user.selectOptions(organizationSelect, "7");

    await waitFor(() => {
      expect(leadsApi.listLeads).toHaveBeenLastCalledWith(7, {
        owner: "",
        search: "",
        status: "",
      });
    });
  });

  it("submits lead creation after client-side validation passes", async () => {
    const user = userEvent.setup();
    render(<LeadsPageClient />);

    await screen.findByText("Qualified Prospect");
    await user.click(screen.getAllByRole("button", { name: "Create lead" })[0]);
    await user.click(screen.getAllByRole("button", { name: "Create lead" })[1]);

    expect(await screen.findByText("Lead name is required.")).toBeInTheDocument();

    await user.type(screen.getByLabelText("Lead name"), "Fresh Lead");
    await user.type(screen.getByLabelText("Lead email"), "fresh@example.com");
    await user.click(screen.getAllByRole("button", { name: "Create lead" })[1]);

    await waitFor(() => {
      expect(leadsApi.createLead).toHaveBeenCalledWith(3, {
        name: "Fresh Lead",
        email: "fresh@example.com",
        phone: "",
        source: "MANUAL",
        status: "NEW",
        owner_id: "",
      });
    });
  });

  it("updates filters and refetches leads", async () => {
    const user = userEvent.setup();
    render(<LeadsPageClient />);

    await screen.findByText("Qualified Prospect");

    await user.selectOptions(screen.getByLabelText("Status filter"), "QUALIFIED");
    await user.type(screen.getByLabelText("Search leads"), "Prospect");

    await waitFor(() => {
      expect(leadsApi.listLeads).toHaveBeenLastCalledWith(3, {
        owner: "",
        search: "Prospect",
        status: "QUALIFIED",
      });
    });
  });
});
