import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function HomePage() {
  const cookieStore = await cookies();
  const hasAccessCookie = cookieStore.has("flowcrm_access");

  redirect(hasAccessCookie ? "/dashboard" : "/login");
}
