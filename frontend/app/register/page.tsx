"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { ApiError } from "@/lib/api-client";
import { register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!form.first_name || !form.last_name || !form.email || !form.password) {
      setError("All fields are required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await register(form);
      setSuccess(`${response.message} You can sign in now.`);
      router.prefetch("/login");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to register.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">FlowCRM</p>
        <h1>Create your account</h1>
        <p className="auth-copy">
          Start with personal access, then join an organization when an admin adds
          you.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            <span>First name</span>
            <input
              autoComplete="given-name"
              value={form.first_name}
              onChange={(event) =>
                setForm((current) => ({ ...current, first_name: event.target.value }))
              }
            />
          </label>

          <label>
            <span>Last name</span>
            <input
              autoComplete="family-name"
              value={form.last_name}
              onChange={(event) =>
                setForm((current) => ({ ...current, last_name: event.target.value }))
              }
            />
          </label>

          <label>
            <span>Email</span>
            <input
              autoComplete="email"
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm((current) => ({ ...current, email: event.target.value }))
              }
            />
          </label>

          <label>
            <span>Password</span>
            <input
              autoComplete="new-password"
              type="password"
              value={form.password}
              onChange={(event) =>
                setForm((current) => ({ ...current, password: event.target.value }))
              }
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}
          {success ? <p className="form-success">{success}</p> : null}

          <button className="primary-button" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create account"}
          </button>
        </form>

        <p className="auth-footer">
          Already registered? <Link href="/login">Go to login</Link>
        </p>
      </section>
    </main>
  );
}
