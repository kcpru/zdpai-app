import { motion, LayoutGroup } from "motion/react";
import React, { useEffect, useId, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import statsLottie from "@assets/lottie/system-solid-10-analytics-hover-analytics.json";
import todoLottie from "@assets/lottie/system-solid-17-assignment-hover-assignment.json";
import adminLottie from "@assets/lottie/system-solid-22-build-hover-build.json";
import homeLottie from "@assets/lottie/system-solid-41-home-hover-pinch.json";
import settingsLottie from "@assets/lottie/system-solid-63-settings-cog-hover-cog-4.json";
import { useAuth } from "@context/AuthContext";
import { usePageTransition } from "@context/PageTransitionContext";

import { NavTab } from "./NavTab";

import "./NavTabs.scss";
import "./NavTab.scss";

export function NavTabs() {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { setTransition, lastTabIndexRef } = usePageTransition();
  const layoutId = useId();

  const tabs = useMemo(() => {
    const base = [
      { label: "Home", path: "/", lottie: homeLottie },
      { label: "Todo", path: "/todo", lottie: todoLottie },
      { label: "Stats", path: "/stats", lottie: statsLottie },
      { label: "Settings", path: "/settings", lottie: settingsLottie },
    ];
    if (user?.isAdmin) {
      base.splice(3, 0, {
        label: "Admin",
        path: "/admin",
        lottie: adminLottie,
      });
    }
    return base;
  }, [user?.isAdmin]);

  const lottieRefs = useMemo(() => tabs.map(() => React.createRef()), [tabs]);

  const handleTabClick = (idx, path) => {
    setTransition(lastTabIndexRef.current, idx);
    navigate(path);
    const ref = lottieRefs[idx];
    if (ref && ref.current) {
      ref.current.stop();
      ref.current.play();
    }
  };

  useEffect(() => {
    const activeIdx = tabs.findIndex((tab) => tab.path === location.pathname);
    const ref = lottieRefs[activeIdx];
    if (activeIdx !== -1 && ref && ref.current) {
      ref.current.stop();
      ref.current.play();
    }
  }, [location.pathname, lottieRefs, tabs]);

  return (
    <LayoutGroup>
      <motion.div className="nav-tabs-header" layoutRoot layoutScroll>
        {tabs.map((tab, idx) => {
          const isActive = location.pathname === tab.path;

          return (
            <NavTab
              key={tab.path}
              idx={idx}
              tab={tab}
              isActive={isActive}
              onClick={() => handleTabClick(idx, tab.path)}
              lottieRef={lottieRefs[idx]}
              layoutId={`${layoutId}-tab-bg`}
            />
          );
        })}
      </motion.div>
    </LayoutGroup>
  );
}
