import { useCallback, useState } from "react";

export function useAuthValidation({
  schema,
  notify,
  setShakeField,
  shakeDuration = 400,
  defaultMessage = "Please check the fields",
}) {
  const [validationErrors, setValidationErrors] = useState({});

  const validate = useCallback(
    (values) => {
      const result = schema.safeParse(values);

      if (result.success) {
        setValidationErrors({});
        return true;
      }

      const flat = result.error.flatten();
      const fieldErrors = Object.entries(flat.fieldErrors).reduce(
        (acc, [key, value]) => {
          if (value?.[0]) acc[key] = value[0];
          return acc;
        },
        {}
      );

      setValidationErrors(fieldErrors);

      const firstError = Object.keys(fieldErrors)[0];
      if (firstError) {
        notify?.({
          type: "error",
          message: fieldErrors[firstError] || defaultMessage,
        });
        if (setShakeField) {
          setShakeField(firstError);
          setTimeout(() => setShakeField(null), shakeDuration);
        }
      }

      return false;
    },
    [schema, notify, setShakeField, shakeDuration, defaultMessage]
  );

  const clearFieldError = useCallback((fieldKey, shouldClear = true) => {
    if (!shouldClear) return;
    setValidationErrors((prev) => {
      if (!prev[fieldKey]) return prev;
      const { [fieldKey]: _removed, ...rest } = prev;
      return rest;
    });
  }, []);

  return {
    validationErrors,
    setValidationErrors,
    validate,
    clearFieldError,
  };
}
