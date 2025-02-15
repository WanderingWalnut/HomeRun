import axios from "axios";

const API_URL = "http://localhost:8000";

export interface Transaction {
  amount: number;
  category: string;
}

export const fetchTransactions = async (): Promise<Transaction[]> => {
  try {
    const response = await axios.get(`${API_URL}/transactions`);
    return response.data.data.transactions;
  } catch (error) {
    console.error("Error fetching transactions:", error);
    return [];
  }
};
