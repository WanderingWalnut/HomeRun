import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  CircularProgress,
  Typography,
  TextField,
} from "@mui/material";
import { motion } from "framer-motion";
import Confetti from "react-confetti";
import Navbar from "../components/Navbar";
import house from "../assets/house.png";

function DiamondProgress({ value = 0, size = 300, strokeWidth = 10 }) {
  const clampedValue = Math.min(100, Math.max(0, value));
  const DIAMOND_PERIMETER = 4 * Math.sqrt(50 ** 2 + 50 ** 2);
  const offset = DIAMOND_PERIMETER - (DIAMOND_PERIMETER * clampedValue) / 100;

  return (
    <Box sx={{ width: size, height: size, mx: "auto" }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 100"
        style={{ overflow: "visible" }}
      >
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
        <path
          d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
          fill="none"
          stroke="#ccc"
          strokeWidth={strokeWidth}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        <path
          d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
          fill="none"
          stroke="url(#diamondGradient)"
          strokeWidth={strokeWidth}
          strokeLinejoin="round"
          strokeLinecap="round"
          strokeDasharray={DIAMOND_PERIMETER}
          strokeDashoffset={offset}
          filter="url(#diamondGlow)"
          style={{ transition: "stroke-dashoffset 0.4s ease" }}
        />
      </svg>
    </Box>
  );
}

export default function MainPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  // User Goal Inputs
  const [housePrice, setHousePrice] = useState<number>(100000); // Default $100,000
  const [downpaymentPercent, setDownpaymentPercent] = useState<number>(20); // Default 20%
  const [years, setYears] = useState<number>(5); // Default 5 years to reach the goal
  const [savedAmount, setSavedAmount] = useState<number>(0);

  const downpaymentGoal = (housePrice * downpaymentPercent) / 100;
  const weeksLeft = years * 52; // Total weeks to reach goal
  const weeklyTarget = downpaymentGoal / weeksLeft; // Weekly savings target

  // Home Run Counter
  const [homeRunsLeft, setHomeRunsLeft] = useState<number>(weeksLeft);
  const [weeklySavings, setWeeklySavings] = useState<number>(0);
  const [weeksGoalHit, setWeeksGoalHit] = useState<number>(0); // New state for tracking weeks goal hit

// Define your Transaction type (you can place this outside your component)
type Transaction = {
  id: string | number;
  name: string;
  merchant_name?: string;
  category?: string[];
  amount: number;
  date: string;
};

// Define a type for the raw Plaid transaction data
type PlaidTransaction = {
  transaction_id: string;
  name: string;
  merchant_name?: string;
  category?: string[];
  amount: number;
  date: string;
};

useEffect(() => {
  const accessToken = "access-sandbox-7984d143-7843-4a42-9c24-956f0fd2e1e5";
  fetch("http://localhost:8000/api/get_transactions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ access_token: accessToken }),
  })
    .then((res) => res.json())
    .then((data) => {
      // Define your dummy transactions (typed as Transaction[])
      const dummyTransactions: Transaction[] = [
        {
          id: "dummy1",
          name: "Paycheck",
          merchant_name: "Home Depot",
          category: ["Employer", "Brick & Mortar"],
          amount: 1525.5,
          date: "2025-02-10",
        },
        {
          id: "dummy2",
          name: "E-Transfer",
          merchant_name: "Friend",
          category: ["Test", "Dummy"],
          amount: 100,
          date: "2025-02-09",
        },
        // You can add more dummy transactions as needed.
      ];

      // Format the real transactions returned by the API.
      let formatted: Transaction[] = [];
      if (
        data.spending_transactions &&
        Array.isArray(data.spending_transactions)
      ) {
        formatted = (data.spending_transactions as PlaidTransaction[]).map(
          (txn, index: number): Transaction => ({
            id: txn.transaction_id || index,
            name: txn.name || "No Name",
            merchant_name: txn.merchant_name || "",
            category: txn.category || [],
            amount: txn.amount,
            date: txn.date,
          })
        );
      }

      // Log for debugging
      console.log("Formatted real transactions:", formatted);

      // Merge dummy transactions regardless of real data length.
      const transactionsWithDummies: Transaction[] = [
        ...formatted,
        ...dummyTransactions,
      ];
      console.log("Merged transactions (with dummies):", transactionsWithDummies);

      setTransactions(transactionsWithDummies);
      setLoading(false);
    })
    .catch((err) => {
      console.error("Error fetching transactions:", err);
      setLoading(false);
    });
}, []);



  // Calculate the total saved amount from transactions.
  useEffect(() => {
    let totalSaved = 0;
    transactions.forEach((txn) => {
      totalSaved += txn.amount;
    });
    setSavedAmount(totalSaved);

    // Calculate weekly savings using local storage to track the week.
    const today = new Date();
    const currentWeek = Math.floor(today.getTime() / (1000 * 60 * 60 * 24 * 7));
    const lastSavedWeek = localStorage.getItem("lastSavedWeek");

    if (lastSavedWeek && Number(lastSavedWeek) === currentWeek) {
      setWeeklySavings((prev) => prev + totalSaved);
    } else {
      localStorage.setItem("lastSavedWeek", String(currentWeek));
      setWeeklySavings(totalSaved);
    }
  }, [transactions]);

  const progress = Math.min(100, (savedAmount / downpaymentGoal) * 100);

  // Check if weekly target is met.
  useEffect(() => {
    if (weeklySavings >= weeklyTarget) {
      setHomeRunsLeft((prev) => Math.max(0, prev - 1));
      setWeeklySavings(0);
      setWeeksGoalHit((prev) => prev + 1); // Increment weeks goal hit
    }
  }, [weeklySavings, weeklyTarget]);

  return (
    <Box>
      <Navbar />
      {progress >= 100 && <Confetti />}

      {/* Wrapper for Home Buying Goal and Weekly Target */}
      <Box display="flex" justifyContent="center" gap={3} mt={10}>
        {/* User Goal Inputs */}
        <Paper
          elevation={3}
          sx={{
            width: "80%",
            p: 3,
            borderRadius: "10px",
          }}
        >
          <Typography variant="h5" fontWeight="bold" mb={2} color="black">
            Set Your Home Buying Goal
          </Typography>
          <Box display="flex" gap={3}>
            <TextField
              label="Total House Price ($)"
              type="number"
              fullWidth
              value={housePrice}
              onChange={(e) => setHousePrice(Number(e.target.value))}
            />
            <TextField
              label="Downpayment (%)"
              type="number"
              fullWidth
              value={downpaymentPercent}
              onChange={(e) => setDownpaymentPercent(Number(e.target.value))}
            />
            <TextField
              label="Years to Save"
              type="number"
              fullWidth
              value={years}
              onChange={(e) => setYears(Number(e.target.value))}
            />
          </Box>
          <Typography variant="body1" color="textSecondary" mt={2}>
            Downpayment Goal:{" "}
            <strong>${downpaymentGoal.toLocaleString()}</strong> | Weeks Left:{" "}
            <strong>{homeRunsLeft}</strong> | Weekly Target:{" "}
            <strong>${weeklyTarget.toFixed(2)}</strong>
          </Typography>
        </Paper>

        {/* Weekly Target Hit Section */}
        <Paper
          elevation={3}
          sx={{
            width: "20%",
            p: 3,
            borderRadius: "10px",
            backgroundColor: "#f7e3b5",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Typography variant="h5" fontWeight="bold" textAlign="center">
            🎯 Weekly Target Hit: <strong>{weeksGoalHit}</strong> Weeks
          </Typography>
        </Paper>
      </Box>

      {/* Main Content */}
      <Box display="flex" justifyContent="center" gap={4} px={4} mt={3}>
        {/* Transactions Panel */}
        <Paper
          elevation={3}
          sx={{
            width: "100%",
            height: "440px",
            p: 3,
            borderRadius: "10px",
            backgroundColor: "white",
            overflowY: "auto",
          }}
        >
          <Typography variant="h5" fontWeight="bold" mb={2} color="black">
            Recent Transactions
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : transactions.length > 0 ? (
            transactions.map((txn) => (
              <motion.div
                key={txn.id}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                style={{
                  marginBottom: "10px",
                  padding: "10px",
                  borderRadius: "8px",
                  backgroundColor: txn.amount < 0 ? "#ffebee" : "#e8f5e9",
                }}
              >
                <Typography variant="body1" fontWeight="bold">
                  {txn.name}
                </Typography>
                {txn.merchant_name && (
                  <Typography variant="body2" color="textSecondary">
                    Merchant: {txn.merchant_name}
                  </Typography>
                )}
                {txn.category && txn.category.length > 0 && (
                  <Typography variant="body2" color="textSecondary">
                    Category: {txn.category.join(" > ")}
                  </Typography>
                )}
                <Typography variant="body2">
                  {txn.amount < 0 ? "-" : "+"}${Math.abs(txn.amount).toFixed(2)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Date: {txn.date}
                </Typography>
              </motion.div>
            ))
          ) : (
            <Typography>No transactions found.</Typography>
          )}
        </Paper>

        {/* Progress Panel */}
        <Paper elevation={3} sx={{ width: "800px", height: "440px", p: 3 }}>
          <Typography variant="h5" fontWeight="bold" mb={2} textAlign="center">
            Progress ({progress.toFixed(2)}%)
          </Typography>
          <DiamondProgress value={progress} size={350} strokeWidth={6} />
        </Paper>
      </Box>
    </Box>
  );
}
