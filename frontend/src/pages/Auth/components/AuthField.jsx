import { motion } from "motion/react";

import { Input } from "@components/Input";

export function AuthField({
  id,
  fieldKey,
  label,
  icon,
  type = "text",
  value,
  onChange,
  placeholder,
  isLoading,
  hasError,
  isValid,
  getFieldMotion,
  delay,
  required = true,
}) {
  const className = `form-group ${
    hasError ? "invalid" : isValid ? "valid" : ""
  }`;

  return (
    <motion.div className={className} {...getFieldMotion(fieldKey, delay)}>
      <label htmlFor={id}>
        {icon} {label}
      </label>
      <Input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        withRipple
        disabled={isLoading}
        required={required}
      />
    </motion.div>
  );
}
