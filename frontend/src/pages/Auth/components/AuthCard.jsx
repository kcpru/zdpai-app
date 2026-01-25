import { motion } from "motion/react";

import { ANIMATION_CONFIG } from "@constants/animations";

export function AuthCard({ icon, title, subtitle, children }) {
  return (
    <div className="auth-container">
      <motion.div className="auth-card" {...ANIMATION_CONFIG.authCard}>
        <div className="auth-header">
          <motion.div className="auth-icon" {...ANIMATION_CONFIG.authIcon}>
            {icon}
          </motion.div>
          <h1 className="auth-title">{title}</h1>
          <p className="auth-subtitle">{subtitle}</p>
        </div>
        {children}
      </motion.div>
    </div>
  );
}
