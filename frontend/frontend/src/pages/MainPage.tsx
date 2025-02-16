import React, { useState, useEffect } from "react";
import { Box, Paper, CircularProgress, Typography, Button } from "@mui/material";
import { motion } from "framer-motion";
import Navbar from "../components/Navbar"; // Import the Navbar component

// Mock transaction data (Replace this with actual API call to backend fetching Plaid data)
const mockTransactions = [
  { id: 1, description: "Grocery Store", amount: -50.25, date: "2025-02-14" },
  { id: 2, description: "Paycheck Deposit", amount: 1500, date: "2025-02-14" },
  { id: 3, description: "Electric Bill", amount: -100, date: "2025-02-13" },
  { id: 4, description: "Amazon Purchase", amount: -75.5, date: "2025-02-12" },
];

/**
 * FANCY DIAMOND PROGRESS COMPONENT
 * Uses a gradient stroke with a subtle glow.
 */
function DiamondProgress({ value = 0, size = 300, strokeWidth = 10 }) {
  // Clamp value between 0–100
  const clampedValue = Math.min(100, Math.max(0, value));

  // Each side of the diamond is ~70.71; total perimeter ~282.84
  const DIAMOND_PERIMETER = 4 * Math.sqrt(50 ** 2 + 50 ** 2);
  // strokeDashoffset controls how much of the stroke is NOT shown
  const offset = DIAMOND_PERIMETER - (DIAMOND_PERIMETER * clampedValue) / 100;

  return (
    <Box sx={{ width: size, height: size, mx: "auto" }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 100"
        style={{ overflow: "visible" }}
      >
        {/* DEFINITIONS: gradient + glow filter */}
        <defs>
          {/* Linear gradient from top-left (#FF6CAB) to bottom-right (#7366FF) */}
          <linearGradient id="diamondGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#FF6CAB" />
            <stop offset="100%" stopColor="#7366FF" />
          </linearGradient>

          {/* Glow filter */}
          <filter id="diamondGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background stroke (light gray) */}
        <path
          d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
          fill="none"
          stroke="#ccc"
          strokeWidth={strokeWidth}
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Foreground stroke (gradient + glow) */}
        <path
          d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
          fill="none"
          stroke="url(#diamondGradient)"   // Apply the linear gradient
          strokeWidth={strokeWidth}
          strokeLinejoin="round"
          strokeLinecap="round"
          strokeDasharray={DIAMOND_PERIMETER}
          strokeDashoffset={offset}
          filter="url(#diamondGlow)"        // Apply the glow filter
          style={{
            transition: "stroke-dashoffset 0.4s ease",
          }}
        />
      </svg>
    </Box>
  );
}

export default function MainPage() {
  type Transaction = {
    id: number;
    description: string;
    amount: number;
    date: string;
  };

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(25);

  useEffect(() => {
    // Simulate API Call
    setTimeout(() => {
      setTransactions(mockTransactions);
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <Box>
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <Box display="flex" justifyContent="center" gap={4} p={4}>
        {/* Transaction Notifications */}
        <Paper elevation={3} sx={{ width: "500px", height: "600px", p: 3 }}>
          <Typography variant="h5" fontWeight="bold" mb={2}>
            Recent Transactions
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            transactions.map((txn) => (
              <motion.div
                key={txn.id}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                style={{
                  marginBottom: "10px",
                  padding: "8px",
                  borderRadius: "5px",
                  backgroundColor: txn.amount < 0 ? "#ffebee" : "#e8f5e9",
                }}
              >
                <Typography variant="body1" fontWeight="bold">
                  {txn.description}
                </Typography>
                <Typography
                  variant="body2"
                  color={txn.amount < 0 ? "error" : "success.main"}
                >
                  {txn.amount < 0 ? "-" : "+"}${Math.abs(txn.amount).toFixed(2)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {txn.date}
                </Typography>
              </motion.div>
            ))
          )}
        </Paper>

        {/* Diamond Progress Panel */}
        <Paper
          elevation={3}
          sx={{
            width: "800px",
            height: "600px",
            p: 3,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Typography variant="h5" fontWeight="bold" mb={2} textAlign="center">
            Progress ({progress}%)
          </Typography>
          {/* Centering the diamond */}
          <Box
            sx={{
              flexGrow: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <DiamondProgress value={progress} size={400} strokeWidth={8} />
          </Box>
          <Box display="flex" justifyContent="center" gap={2} mt={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setProgress((prev) => Math.max(0, prev - 10))}
            >
              Decrease
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setProgress((prev) => Math.min(100, prev + 10))}
            >
              Increase
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
}
