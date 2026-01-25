import { useState } from "react";

import { ANIMATION_CONFIG } from "@constants/animations";

export function useAuthFormMotion() {
  const [shakeField, setShakeField] = useState(null);

  const getFieldMotion = (field, delay) => {
    const base = ANIMATION_CONFIG.authFormGroup(delay);
    const isShaking = shakeField === field;

    if (isShaking) {
      return {
        initial: { opacity: 1, x: 0 },
        animate: { ...base.animate, ...ANIMATION_CONFIG.shake.animate },
        transition: { ...ANIMATION_CONFIG.shake.transition },
      };
    }

    return base;
  };

  return { getFieldMotion, shakeField, setShakeField };
}
