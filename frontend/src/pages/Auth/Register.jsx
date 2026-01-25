import { motion } from "motion/react";
import { useState } from "react";
import {
  MdPersonAdd,
  MdMailOutline,
  MdLockOutline,
  MdCheckCircleOutline,
} from "react-icons/md";
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

export function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { getFieldMotion, setShakeField } = useAuthFormMotion();
  const { register, error } = useAuth();
  const navigate = useNavigate();
  const { notify } = useNotifications();

  const registerSchema = z
    .object({
      username: z.string().trim().min(3, "Username too short"),
      email: z.string().trim().email("Invalid email"),
      password: z
        .string()
        .trim()
        .min(6, "Password must be at least 6 characters"),
      passwordConfirm: z.string().trim().min(1, "Required"),
    })
    .refine((data) => data.password === data.passwordConfirm, {
      message: "Passwords do not match",
      path: ["passwordConfirm"],
    });

  const { validationErrors, validate, clearFieldError } = useAuthValidation({
    schema: registerSchema,
    notify,
    setShakeField,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const isValid = validate({
      username,
      email,
      password,
      passwordConfirm,
    });

    if (!isValid) {
      return;
    }

    setIsLoading(true);
    const success = await register(username, email, password);
    setIsLoading(false);

    if (success) {
      navigate("/");
    } else if (error) {
      notify({ type: "error", message: error });
    } else {
      notify({ type: "error", message: "Registration failed" });
    }
  };

  return (
    <AuthCard
      icon={<MdPersonAdd />}
      title="Join the Revolution!"
      subtitle="Join and start organizing tasks"
    >
      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        <AuthField
          id="username"
          fieldKey="username"
          label="Username"
          icon={<MdPersonAdd className="form-icon" />}
          value={username}
          onChange={(e) => {
            const value = e.target.value;
            setUsername(value);
            clearFieldError("username", value.trim().length >= 3);
          }}
          placeholder="your_awesome_name"
          isLoading={isLoading}
          hasError={!!validationErrors.username}
          isValid={username.trim().length >= 3}
          getFieldMotion={getFieldMotion}
          delay={0.2}
        />

        <AuthField
          id="email"
          fieldKey="email"
          label="Email"
          icon={<MdMailOutline className="form-icon" />}
          type="email"
          value={email}
          onChange={(e) => {
            const value = e.target.value;
            setEmail(value);
            if (validationErrors.email && value.trim()) {
              const isValidEmail = z
                .string()
                .email()
                .safeParse(value.trim()).success;
              clearFieldError("email", isValidEmail);
            }
          }}
          placeholder="your@email.com"
          isLoading={isLoading}
          hasError={!!validationErrors.email}
          isValid={!!email.trim()}
          getFieldMotion={getFieldMotion}
          delay={0.3}
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
            clearFieldError("password", value.trim().length >= 6);
          }}
          placeholder="••••••••"
          isLoading={isLoading}
          hasError={!!validationErrors.password}
          isValid={password.trim().length >= 6}
          getFieldMotion={getFieldMotion}
          delay={0.4}
        />

        <AuthField
          id="passwordConfirm"
          fieldKey="passwordConfirm"
          label="Confirm Password"
          icon={<MdCheckCircleOutline className="form-icon" />}
          type="password"
          value={passwordConfirm}
          onChange={(e) => {
            const value = e.target.value;
            setPasswordConfirm(value);
            clearFieldError(
              "passwordConfirm",
              value.trim() && value.trim() === password.trim()
            );
          }}
          placeholder="Confirm password"
          isLoading={isLoading}
          hasError={!!validationErrors.passwordConfirm}
          isValid={!!passwordConfirm.trim() && passwordConfirm === password}
          getFieldMotion={getFieldMotion}
          delay={0.5}
        />

        <motion.div {...ANIMATION_CONFIG.authButton(0.6)}>
          <Button
            type="submit"
            className="auth-button"
            disabled={isLoading}
            size="md"
            icon={<MdPersonAdd />}
          >
            {isLoading ? "Creating account..." : "Create Account"}
          </Button>
        </motion.div>
      </form>

      <motion.p className="auth-link" {...ANIMATION_CONFIG.authButton(0.7)}>
        Already have an account? <Link to="/login">Sign in here</Link>
      </motion.p>

      <motion.div
        className="auth-benefits"
        {...ANIMATION_CONFIG.authButton(0.8)}
      >
        <p>🚀 Start crushing tasks</p>
        <p>🧭 Build momentum with habits</p>
        <p>🎮 Level up your productivity</p>
      </motion.div>
    </AuthCard>
  );
}
