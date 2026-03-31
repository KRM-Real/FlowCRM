export type MembershipSummary = {
  id: number;
  organization_id: number;
  organization_name: string;
  organization_slug: string;
  role: string;
};

export type AuthUser = {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  memberships: MembershipSummary[];
};

export type LoginInput = {
  email: string;
  password: string;
};

export type RegisterInput = {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
};
