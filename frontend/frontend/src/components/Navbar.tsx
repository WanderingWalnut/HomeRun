import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import logo from "../assets/logo.png";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any stored tokens or state
    localStorage.removeItem("plaid_access_token");
    localStorage.removeItem("lastSavedWeek");

    // Log the action
    console.log("Logging out...");

    // Navigate to home page
    navigate("/");
  };

  return (
    <AppBar
      position="absolute"
      sx={{
        top: 0,
        left: 0,
        width: "100%",
        zIndex: 1100,
        bgcolor: "linear-gradient(90deg, #ff6cab 0%, #7366ff 100%)",
        boxShadow: "0px 4px 12px rgba(0,0,0,0.3)",
      }}
    >
      <Toolbar>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography
            variant="h5"
            sx={{
              display: "flex",
              alignItems: "center",
              fontWeight: "bold",
              color: "white",
            }}
          >
            <img
              src={logo}
              alt="Logo"
              style={{
                height: "50px",
                marginRight: "15px",
                borderRadius: "8px",
                border: "2px solid white",
              }}
            />
            HomeRun
          </Typography>
        </motion.div>

        <Box sx={{ flexGrow: 1 }} />

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Button
            color="inherit"
            onClick={handleLogout}
            sx={{
              fontWeight: "bold",
              fontSize: "16px",
              backgroundColor: "rgba(255,255,255,0.2)",
              borderRadius: "8px",
              px: 3,
              "&:hover": {
                backgroundColor: "rgba(255,255,255,0.4)",
                color: "#ff6c6c",
              },
            }}
          >
            Logout
          </Button>
        </motion.div>
      </Toolbar>
    </AppBar>
  );
}
