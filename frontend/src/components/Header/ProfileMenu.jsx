import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState, useRef } from "react";
import { createPortal } from "react-dom";
import { MdLightMode, MdDarkMode, MdLogout, MdSettings } from "react-icons/md";
import { useNavigate } from "react-router-dom";

import { ANIMATION_CONFIG } from "@constants/animations";
import { useAuth } from "@context/AuthContext";
import { useTheme } from "@context/ThemeContext";
import { useClickOutside } from "@hooks/useClickOutside";

import { Button } from "../Button";
import "./ProfileMenu.scss";

export function ProfileMenu() {
  const navigate = useNavigate();
  const [showProfile, setShowProfile] = useState(false);
  const { user, logout, avatarUrl, fetchAvatarUrl } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const profileRef = useRef(null);
  const dropdownRef = useRef(null);

  useClickOutside(profileRef, () => setShowProfile(false), {
    ignoreSelf: true,
    ignoreRefs: [dropdownRef],
  });

  useEffect(() => {
    if (user?.id) {
      fetchAvatarUrl();
    }
  }, [user?.id, fetchAvatarUrl]);

  return (
    <div className="profile-container" ref={profileRef}>
      <button
        className="profile-avatar-btn"
        onClick={() => setShowProfile(!showProfile)}
        title={user?.username}
        type="button"
      >
        {avatarUrl ? (
          <img
            className="profile-avatar"
            src={avatarUrl}
            alt="avatar"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "";
            }}
          />
        ) : (
          <span className="profile-avatar-fallback">
            {user?.username?.charAt(0).toUpperCase() || "U"}
          </span>
        )}
      </button>

      {createPortal(
        <AnimatePresence>
          {showProfile && (
            <motion.div
              ref={dropdownRef}
              className="dropdown-menu"
              {...ANIMATION_CONFIG.dropdown}
            >
              <div className="profile-info">
                <div className="profile-username">{user?.username}</div>
                <div className="profile-email">{user?.email}</div>
              </div>
              <div className="profile-buttons">
                <Button
                  variant="secondary"
                  size="md"
                  onClick={toggleTheme}
                  title={isDarkMode ? "Light Mode" : "Dark Mode"}
                  icon={isDarkMode ? <MdLightMode /> : <MdDarkMode />}
                >
                  {isDarkMode ? "Light" : "Dark"}
                </Button>
                <Button
                  variant="secondary"
                  size="md"
                  onClick={() => navigate("/settings")}
                  icon={<MdSettings />}
                >
                  Settings
                </Button>
                {user?.isAdmin && (
                  <Button
                    variant="secondary"
                    size="md"
                    onClick={() => navigate("/admin")}
                    icon={<MdSettings />}
                  >
                    Admin
                  </Button>
                )}
                <Button
                  variant="danger"
                  size="md"
                  onClick={() => {
                    logout();
                    navigate("/login");
                  }}
                  icon={<MdLogout />}
                >
                  Logout
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </div>
  );
}

export default ProfileMenu;
