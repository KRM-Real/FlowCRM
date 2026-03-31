"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import { getCurrentUser, logout } from "@/lib/auth";
import type { AuthUser } from "@/types/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      try {
        const currentUser = await getCurrentUser();
        if (isMounted) {
          setUser(currentUser);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof ApiError ? err.message : "Unable to load account.");
          router.replace("/login");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadUser();

    return () => {
      isMounted = false;
    };
  }, [router]);

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await logout();
    } finally {
      router.replace("/login");
      router.refresh();
    }
  }

  if (isLoading) {
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
          <p className="form-error">{error ?? "Authentication required."}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="dashboard-page">
      <section className="dashboard-shell">
        <div className="dashboard-hero">
          <div>
            <p className="eyebrow">Dashboard</p>
            <h1>
              {user.first_name} {user.last_name}
            </h1>
            <p className="dashboard-muted">{user.email}</p>
          </div>

          <button
            className="secondary-button"
            disabled={isLoggingOut}
            onClick={handleLogout}
            type="button"
          >
            {isLoggingOut ? "Signing out..." : "Logout"}
          </button>
        </div>

        <section className="dashboard-card">
          <h2>Organization access</h2>
          {user.memberships.length === 0 ? (
            <p className="dashboard-muted">
              No organization memberships yet. An admin can add you from the members
              area.
            </p>
          ) : (
            <div className="membership-grid">
              {user.memberships.map((membership) => (
                <article className="membership-card" key={membership.id}>
                  <p className="membership-role">{membership.role}</p>
                  <h3>{membership.organization_name}</h3>
                  <p>{membership.organization_slug}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
