import { useEffect, useState } from "react";
import { fetchTransactions, Transaction } from "./services/api";

function App() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    fetchTransactions().then((data) => setTransactions(data));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6">🏡 Hackathon Savings Tracker</h1>
      
      <div className="bg-white p-4 shadow-md rounded-md w-full max-w-md">
        <h2 className="text-lg font-semibold">Recent Transactions</h2>
        {transactions.length > 0 ? (
          <ul className="mt-2">
            {transactions.map((tx, index) => (
              <li key={index} className="p-2 border-b">
                Spent <b>${tx.amount}</b> on <i>{tx.category}</i>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 mt-2">No transactions found.</p>
        )}
      </div>
    </div>
  );
}

export default App;
