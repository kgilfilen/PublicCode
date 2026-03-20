// Provides hidden/access-controlled route for Admin page, etc
import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";

const ROLE_CLAIM = "https://meetwomenbetter.com/roles";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading, loginWithRedirect, user } = useAuth0();

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      loginWithRedirect({
        authorizationParams: {
          redirect_uri: window.location.origin + "/admin",
        },
      });
    }
  }, [isLoading, isAuthenticated, loginWithRedirect]);

  if (isLoading) {
    return <div style={{ padding: "2rem" }}>Checking access...</div>;
  }

  if (!isAuthenticated) {
    return null;
  }

  // Normalizes roles to lowercase to avoid "Admin" vs "admin" issues
  const roles = (user?.[ROLE_CLAIM] || []).map(role =>
    String(role).toLowerCase()
  );

  const isAdmin = roles.includes("admin");

  if (!isAdmin) {
    return (
      <div style={{ padding: "2rem", color: "#f44336" }}>
        Access denied. Admins only.
      </div>
    );
  }

  return children;
}
