import React, { useState, useEffect } from "react";
import { Box, Paper, CircularProgress, Typography, Button } from "@mui/material";
import { motion } from "framer-motion";
import Confetti from 'react-confetti';
import Navbar from "../components/Navbar";
import house from "../assets/house.png";

const mockTransactions = [
  { id: 1, description: "Grocery Store", amount: -50.25, date: "2025-02-14" },
  { id: 2, description: "Paycheck Deposit", amount: 1500, date: "2025-02-14" },
  { id: 3, description: "Electric Bill", amount: -100, date: "2025-02-13" },
  { id: 4, description: "Amazon Purchase", amount: -75.5, date: "2025-02-12" },
];

function DiamondProgress({ value = 0, size = 300, strokeWidth = 10 }) {
  const clampedValue = Math.min(100, Math.max(0, value));
  const DIAMOND_PERIMETER = 4 * Math.sqrt(50 ** 2 + 50 ** 2);
  const offset = DIAMOND_PERIMETER - (DIAMOND_PERIMETER * clampedValue) / 100;

  return (
    <Box sx={{ width: size, height: size, mx: "auto" }}>
      <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ overflow: "visible" }}>
        <defs>
          <linearGradient id="diamondGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#FF6CAB" />
            <stop offset="100%" stopColor="#7366FF" />
          </linearGradient>
          <filter id="diamondGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <image href={house} x="-1" y="13" height="67" width="100" opacity="1" />
        <path d="M 50,0 L 100,50 L 50,100 L 0,50 Z" fill="none" stroke="#ccc" strokeWidth={strokeWidth} strokeLinejoin="round" strokeLinecap="round" />
        <path d="M 50,0 L 100,50 L 50,100 L 0,50 Z" fill="none" stroke="url(#diamondGradient)" strokeWidth={strokeWidth} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={DIAMOND_PERIMETER} strokeDashoffset={offset} filter="url(#diamondGlow)" style={{ transition: "stroke-dashoffset 0.4s ease" }} />
      </svg>
    </Box>
  );
}

export default function MainPage() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(25);

  useEffect(() => {
    setTimeout(() => {
      setTransactions(mockTransactions);
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <Box>
      <Navbar />
      {progress === 100 && <Confetti />} 
      <Box display="flex" justifyContent="center" gap={4} p={4}>
        <Paper elevation={3} sx={{ width: "500px", height: "600px", p: 3, borderRadius: "10px", backgroundColor: "white" }}>
          <Typography variant="h5" fontWeight="bold" mb={2} color="black">Recent Transactions</Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            transactions.map((txn) => (
              <motion.div key={txn.id} initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }} style={{ display: "flex", alignItems: "center", marginBottom: "12px", padding: "12px", borderRadius: "8px", backgroundColor: txn.amount < 0 ? "#ffebee" : "#e8f5e9", boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.1)" }}>
                <i className={txn.amount < 0 ? "bi bi-cart-x text-danger" : "bi bi-wallet text-success"} style={{ fontSize: "18px", marginRight: "12px" }}></i>
                <Box>
                  <Typography variant="body1" fontWeight="bold">{txn.description}</Typography>
                  <Typography variant="body2" color={txn.amount < 0 ? "error" : "success.main"}>{txn.amount < 0 ? "-" : "+"}${Math.abs(txn.amount).toFixed(2)}</Typography>
                  <Typography variant="caption" color="textSecondary">{txn.date}</Typography>
                </Box>
              </motion.div>
            ))
          )}
        </Paper>
        <Paper elevation={3} sx={{ width: "800px", height: "600px", p: 3, display: "flex", flexDirection: "column" }}>
          <Typography variant="h5" fontWeight="bold" mb={2} textAlign="center">Progress ({progress}%)</Typography>
          <Box sx={{ flexGrow: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <DiamondProgress value={progress} size={400} strokeWidth={7} />
          </Box>
          <Box display="flex" justifyContent="center" gap={2} mt={2}>
            <Button variant="contained" color="primary" onClick={() => setProgress((prev) => Math.max(0, prev - 10))}>Decrease</Button>
            <Button variant="contained" color="primary" onClick={() => setProgress((prev) => Math.min(100, prev + 10))}>Increase</Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
}
