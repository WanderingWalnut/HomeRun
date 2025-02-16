import React from "react";
import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import logo from "../assets/logo.png"
export default function Navbar() {
  const handleLogout = () => {
    console.log("Logging out...");
    // Add logout logic here
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        top: 0, left: 0, width: "100%", zIndex: 1100,
        bgcolor: "black",
        boxShadow: "0px 2px 10px rgba(0, 0, 0, 0.3)"
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          sx={{ flexGrow: 1, display: "flex", alignItems: "center" }}
        >
          <img src={logo} alt="Logo" style={{ height: "40px", marginRight: "10px", borderRadius: "5px" }} />
          Dashboard
        </Typography>

        <div className="d-flex justify-content-end">
          <Button color="inherit" onClick={handleLogout} sx={{ fontWeight: "bold", fontSize: "16px", "&:hover": { color: "#ff6c6c" } }}>
            Logout
          </Button>
        </div>
      </Toolbar>
    </AppBar>
    // <AppBar position="fixed" sx={{ top: 0, left: 0, width: "100%", zIndex: 1100, bgcolor: "black" }}>
    //   <Toolbar>
    //     <Typography variant="h6" sx={{ flexGrow: 1, display: "flex", alignItems: "center" }}>
    //       <img src={logo} alt="Logo" style={{ height: "50px", marginRight: "10px" }} />

    //     </Typography>
    //     <div className="d-flex justify-content-end">
    //       <Button color="inherit" onClick={handleLogout}>
    //         Logout
    //       </Button>
    //     </div>
    //   </Toolbar>
    // </AppBar>
  );
}
