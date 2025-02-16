import React, { useState, useEffect } from "react";
import { Box, Paper, CircularProgress, Typography, Button } from "@mui/material";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import Navbar from "../components/Navbar"; // Import the Navbar component

// Mock transaction data (Replace this with actual API call to backend fetching Plaid data)
const mockTransactions = [
  { id: 1, description: "Grocery Store", amount: -50.25, date: "2025-02-14" },
  { id: 2, description: "Paycheck Deposit", amount: 1500, date: "2025-02-14" },
  { id: 3, description: "Electric Bill", amount: -100, date: "2025-02-13" },
  { id: 4, description: "Amazon Purchase", amount: -75.5, date: "2025-02-12" },
];

// Mock financial data for animation
const mockChartData = [
  { name: "Jan", savings: 500 },
  { name: "Feb", savings: 750 },
  { name: "Mar", savings: 300 },
  { name: "Apr", savings: 900 },
];

export default function MainPage() {
  type Transaction = {
    id: number;
    description: string;
    amount: number;
    date: string;
  };
  
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

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
        <Paper elevation={3} sx={{ width: "400px", p: 3 }}>
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
                style={{ marginBottom: "10px", padding: "8px", borderRadius: "5px", backgroundColor: txn.amount < 0 ? "#ffebee" : "#e8f5e9" }}
              >
                <Typography variant="body1" fontWeight="bold">
                  {txn.description}
                </Typography>
                <Typography variant="body2" color={txn.amount < 0 ? "error" : "success.main"}>
                  {txn.amount < 0 ? "-" : "+"}${Math.abs(txn.amount).toFixed(2)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {txn.date}
                </Typography>
              </motion.div>
            ))
          )}
        </Paper>

        {/* Animated Chart for Financial Data */}
        <Paper elevation={3} sx={{ width: "500px", height: "300px", p: 3 }}>
          <Typography variant="h5" fontWeight="bold" mb={2}>
            Savings Overview
          </Typography>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={mockChartData}>
              <XAxis dataKey="name" stroke="#8884d8" />
              <YAxis stroke="#8884d8" />
              <Tooltip />
              <Bar dataKey="savings" fill="#8884d8" animationDuration={800} />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    </Box>
  );
}
