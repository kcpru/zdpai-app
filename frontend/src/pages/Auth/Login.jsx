import { motion } from "motion/react";
import { useState } from "react";
import { MdLogin, MdMailOutline, MdLockOutline } from "react-icons/md";
import { useNavigate, Link } from "react-router-dom";
import { z } from "zod";

import { Button } from "@components/Button";
import { ANIMATION_CONFIG } from "@constants/animations";
import { useAuth } from "@context/AuthContext";
import { useNotifications } from "@context/NotificationsContext";
import { AuthCard } from "@pages/Auth/components/AuthCard";
import { AuthField } from "@pages/Auth/components/AuthField";
import { useAuthFormMotion } from "@pages/Auth/hooks/useAuthFormMotion";
import { useAuthValidation } from "@pages/Auth/hooks/useAuthValidation";

import "./Auth.scss";

export function Login() {
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { getFieldMotion, setShakeField } = useAuthFormMotion();
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const { notify } = useNotifications();

  const loginSchema = z.object({
    login: z.string().trim().min(1, "Required"),
    password: z
      .string()
      .trim()
      .min(8, "Password must be at least 8 characters"),
  });

  const { validationErrors, validate, clearFieldError } = useAuthValidation({
    schema: loginSchema,
    notify,
    setShakeField,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const isValid = validate({
      login: usernameOrEmail,
      password,
    });

    if (!isValid) {
      return;
    }

    setIsLoading(true);
    const success = await login(usernameOrEmail, password);
    setIsLoading(false);

    if (success) {
      navigate("/");
    } else if (error) {
      notify({ type: "error", message: error });
    } else {
      notify({ type: "error", message: "Invalid credentials" });
    }
  };

  return (
    <AuthCard
      icon={<MdLogin />}
      title="Welcome Back!"
      subtitle="Sign in to your todo chaos"
    >
      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        <AuthField
          id="login"
          fieldKey="login"
          label="Username or Email"
          icon={<MdMailOutline className="form-icon" />}
          value={usernameOrEmail}
          onChange={(e) => {
            const value = e.target.value;
            setUsernameOrEmail(value);
            clearFieldError("login", value.trim());
          }}
          placeholder="your@email.com"
          isLoading={isLoading}
          hasError={!!validationErrors.login}
          isValid={!!usernameOrEmail.trim()}
          getFieldMotion={getFieldMotion}
          delay={0.2}
        />

        <AuthField
          id="password"
          fieldKey="password"
          label="Password"
          icon={<MdLockOutline className="form-icon" />}
          type="password"
          value={password}
          onChange={(e) => {
            const value = e.target.value;
            setPassword(value);
            clearFieldError("password", value.trim().length >= 8);
          }}
          placeholder="••••••••"
          isLoading={isLoading}
          hasError={!!validationErrors.password}
          isValid={password.trim().length >= 8}
          getFieldMotion={getFieldMotion}
          delay={0.3}
        />

        <motion.div {...ANIMATION_CONFIG.authButton(0.4)}>
          <Button
            type="submit"
            className="auth-button"
            disabled={isLoading}
            size="md"
            icon={<MdLogin />}
          >
            {isLoading ? "Logging in..." : "Sign In"}
          </Button>
        </motion.div>
      </form>

      <motion.p className="auth-link" {...ANIMATION_CONFIG.authButton(0.5)}>
        New to chaos? <Link to="/register">Create an account</Link>
      </motion.p>

      <motion.div
        className="auth-benefits"
        {...ANIMATION_CONFIG.authButton(0.6)}
      >
        <p>✨ Track your chaos</p>
        <p>🎯 Stay focused and productive</p>
        <p>⚡ Build habits</p>
      </motion.div>
    </AuthCard>
  );
}
