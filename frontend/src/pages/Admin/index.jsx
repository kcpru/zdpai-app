import { useEffect, useState } from "react";

import { Button } from "@components/Button";
import { FilterSelect } from "@components/FilterSelect";
import HeaderRow from "@components/HeaderRow";
import { Input } from "@components/Input";
import { useAuth } from "@context/AuthContext";
import { useNotifications } from "@context/NotificationsContext";

import "./Admin.scss";

export function Admin() {
  const { user, adminListUsers, adminUpdateUser, adminDeleteUser } = useAuth();
  const { notify } = useNotifications();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");

  const roleOptions = [
    { value: "admin", label: "Admin" },
    { value: "user", label: "User" },
  ];

  const filterOptions = [
    { value: "all", label: "All" },
    { value: "admin", label: "Admins" },
    { value: "user", label: "Users" },
  ];

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await adminListUsers();
      setUsers(data || []);
    } catch (err) {
      notify({ message: err.message || "Failed to load users", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  if (!user?.isAdmin) {
    return (
      <div className="admin-page">
        <HeaderRow title="Admin" subtitle="Access denied." />
      </div>
    );
  }

  const handleFieldChange = (id, field, value) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === id ? { ...u, [field]: value, _dirty: true } : u
      )
    );
  };

  const handleSave = async (u) => {
    try {
      const payload = {
        username: u.username,
        email: u.email,
        isAdmin: u.isAdmin,
      };
      const updated = await adminUpdateUser(u.id, payload);
      setUsers((prev) => prev.map((x) => (x.id === u.id ? { ...updated } : x)));
      notify({ message: "User updated", type: "success" });
    } catch (err) {
      notify({
        message: err.message || "Failed to update user",
        type: "error",
      });
    }
  };

  const handleDelete = async (u) => {
    if (!window.confirm(`Delete user ${u.username}?`)) return;
    try {
      await adminDeleteUser(u.id);
      setUsers((prev) => prev.filter((x) => x.id !== u.id));
      notify({ message: "User deleted", type: "success" });
    } catch (err) {
      notify({
        message: err.message || "Failed to delete user",
        type: "error",
      });
    }
  };

  const normalizedQuery = query.trim().toLowerCase();
  const filteredUsers = users.filter((u) => {
    const matchesQuery =
      !normalizedQuery ||
      u.username.toLowerCase().includes(normalizedQuery) ||
      u.email.toLowerCase().includes(normalizedQuery);

    const matchesRole =
      roleFilter === "all" ||
      (roleFilter === "admin" && u.isAdmin) ||
      (roleFilter === "user" && !u.isAdmin);

    return matchesQuery && matchesRole;
  });

  return (
    <div className="admin-page">
      <div className="admin-header">
        <HeaderRow title="Admin" subtitle="Manage users and permissions" />
        <div className="admin-controls">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search username or email"
          />
          <FilterSelect
            options={filterOptions}
            value={roleFilter}
            onChange={setRoleFilter}
            ariaLabel="Filter users"
          />
          <Button onClick={loadUsers} disabled={loading}>
            {loading ? "Loading..." : "Refresh"}
          </Button>
        </div>
      </div>

      <div className="admin-table">
        <div className="admin-row admin-row-head">
          <div>Username</div>
          <div>Email</div>
          <div>Role</div>
          <div>Actions</div>
        </div>
        {filteredUsers.map((u) => (
          <div className="admin-row" key={u.id}>
            <Input
              value={u.username}
              onChange={(e) =>
                handleFieldChange(u.id, "username", e.target.value)
              }
              placeholder="Username"
            />
            <Input
              value={u.email}
              onChange={(e) => handleFieldChange(u.id, "email", e.target.value)}
              placeholder="Email"
            />
            <div className="admin-role-select">
              <FilterSelect
                options={roleOptions}
                value={u.isAdmin ? "admin" : "user"}
                onChange={(value) =>
                  handleFieldChange(u.id, "isAdmin", value === "admin")
                }
                ariaLabel="Select user role"
              />
            </div>
            <div className="admin-actions">
              <Button onClick={() => handleSave(u)}>Save</Button>
              <Button variant="danger" onClick={() => handleDelete(u)}>
                Delete
              </Button>
            </div>
          </div>
        ))}
        {!filteredUsers.length && !loading && (
          <div className="admin-empty">No users found</div>
        )}
      </div>
    </div>
  );
}

export default Admin;
