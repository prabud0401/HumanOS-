import { useState, useEffect } from "react";

interface Transaction {
  id: number;
  type: string;
  category: string;
  amount: number;
  currency: string;
  description: string;
  date: string;
  recurring: boolean;
}

interface Loan {
  id: number;
  name: string;
  total_amount: number;
  remaining_amount: number;
  monthly_payment: number;
  interest_rate: number;
  due_date: string;
  status: string;
}

interface Summary {
  totalIncome: number;
  totalExpense: number;
  net: number;
  savingsRate: number;
  totalDebt: number;
  monthlyLoanPayments: number;
  byCategory: Record<string, number>;
}

export default function Financial() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [loansList, setLoans] = useState<Loan[]>([]);
  const [showTxForm, setShowTxForm] = useState(false);
  const [showLoanForm, setShowLoanForm] = useState(false);
  const [txForm, setTxForm] = useState({
    type: "expense",
    category: "food",
    amount: "",
    description: "",
    date: new Date().toISOString().split("T")[0],
    recurring: false,
  });
  const [loanForm, setLoanForm] = useState({
    name: "",
    totalAmount: "",
    remainingAmount: "",
    monthlyPayment: "",
    interestRate: "",
    dueDate: "",
  });

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const [s, t, l] = await Promise.all([
      fetch("/api/financial/summary").then((r) => r.json()),
      fetch("/api/financial/transactions").then((r) => r.json()),
      fetch("/api/financial/loans").then((r) => r.json()),
    ]);
    setSummary(s);
    setTxns(t);
    setLoans(l);
  }

  async function addTx(e: React.FormEvent) {
    e.preventDefault();
    await fetch("/api/financial/transactions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...txForm, amount: parseFloat(txForm.amount) }),
    });
    setTxForm({ type: "expense", category: "food", amount: "", description: "", date: new Date().toISOString().split("T")[0], recurring: false });
    setShowTxForm(false);
    load();
  }

  async function addLn(e: React.FormEvent) {
    e.preventDefault();
    await fetch("/api/financial/loans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loanForm),
    });
    setLoanForm({ name: "", totalAmount: "", remainingAmount: "", monthlyPayment: "", interestRate: "", dueDate: "" });
    setShowLoanForm(false);
    load();
  }

  async function deleteTx(id: number) {
    await fetch(`/api/financial/transactions/${id}`, { method: "DELETE" });
    load();
  }

  async function deleteLn(id: number) {
    await fetch(`/api/financial/loans/${id}`, { method: "DELETE" });
    load();
  }

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-LK", { style: "decimal", minimumFractionDigits: 2 }).format(n);

  const categories = [
    "food", "rent", "transport", "utilities", "entertainment", "education",
    "health", "clothing", "subscriptions", "loan_payment", "fees",
    "salary", "freelance", "investment", "gift", "refund", "other",
  ];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Financial Sense</h2>
          <p className="text-gray-400 text-sm">Track your money like you track your thoughts.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowTxForm(!showTxForm)} className="bg-bio-600 hover:bg-bio-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            {showTxForm ? "Cancel" : "+ Transaction"}
          </button>
          <button onClick={() => setShowLoanForm(!showLoanForm)} className="bg-neural-700 hover:bg-neural-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            {showLoanForm ? "Cancel" : "+ Loan"}
          </button>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-xs text-gray-500">Income</p>
            <p className="text-xl font-bold text-green-400">LKR {fmt(summary.totalIncome)}</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-xs text-gray-500">Expenses</p>
            <p className="text-xl font-bold text-red-400">LKR {fmt(summary.totalExpense)}</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-xs text-gray-500">Net</p>
            <p className={`text-xl font-bold ${summary.net >= 0 ? "text-bio-400" : "text-red-400"}`}>
              LKR {fmt(summary.net)}
            </p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-xs text-gray-500">Total Debt</p>
            <p className="text-xl font-bold text-yellow-400">LKR {fmt(summary.totalDebt)}</p>
          </div>
        </div>
      )}

      {showTxForm && (
        <form onSubmit={addTx} className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <select value={txForm.type} onChange={(e) => setTxForm({ ...txForm, type: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm">
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
            <select value={txForm.category} onChange={(e) => setTxForm({ ...txForm, category: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm">
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <input type="number" step="0.01" value={txForm.amount} onChange={(e) => setTxForm({ ...txForm, amount: e.target.value })} placeholder="Amount" required className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="date" value={txForm.date} onChange={(e) => setTxForm({ ...txForm, date: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="flex gap-3 mt-3">
            <input value={txForm.description} onChange={(e) => setTxForm({ ...txForm, description: e.target.value })} placeholder="Description (optional)" className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input type="checkbox" checked={txForm.recurring} onChange={(e) => setTxForm({ ...txForm, recurring: e.target.checked })} />
              Recurring
            </label>
            <button type="submit" className="bg-bio-600 hover:bg-bio-500 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">Add</button>
          </div>
        </form>
      )}

      {showLoanForm && (
        <form onSubmit={addLn} className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            <input value={loanForm.name} onChange={(e) => setLoanForm({ ...loanForm, name: e.target.value })} placeholder="Loan name" required className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="number" step="0.01" value={loanForm.totalAmount} onChange={(e) => setLoanForm({ ...loanForm, totalAmount: e.target.value })} placeholder="Total amount" required className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="number" step="0.01" value={loanForm.remainingAmount} onChange={(e) => setLoanForm({ ...loanForm, remainingAmount: e.target.value })} placeholder="Remaining amount" className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="number" step="0.01" value={loanForm.monthlyPayment} onChange={(e) => setLoanForm({ ...loanForm, monthlyPayment: e.target.value })} placeholder="Monthly payment" className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="number" step="0.01" value={loanForm.interestRate} onChange={(e) => setLoanForm({ ...loanForm, interestRate: e.target.value })} placeholder="Interest rate %" className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="date" value={loanForm.dueDate} onChange={(e) => setLoanForm({ ...loanForm, dueDate: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm" />
          </div>
          <button type="submit" className="mt-3 bg-neural-700 hover:bg-neural-600 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">Add Loan</button>
        </form>
      )}

      {loansList.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Loans & Dues</h3>
          <div className="space-y-2">
            {loansList.map((l) => (
              <div key={l.id} className="bg-gray-900 rounded-xl p-4 border border-gray-800 flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm">{l.name}</p>
                  <p className="text-xs text-gray-500">
                    LKR {fmt(l.remaining_amount)} remaining of {fmt(l.total_amount)}
                    {l.monthly_payment > 0 && ` · LKR ${fmt(l.monthly_payment)}/month`}
                    {l.interest_rate > 0 && ` · ${l.interest_rate}% interest`}
                  </p>
                  <div className="mt-2 w-48 bg-gray-800 rounded-full h-1.5">
                    <div
                      className="bg-yellow-500 h-1.5 rounded-full"
                      style={{ width: `${((l.total_amount - l.remaining_amount) / l.total_amount) * 100}%` }}
                    />
                  </div>
                </div>
                <button onClick={() => deleteLn(l.id)} className="text-xs text-gray-600 hover:text-red-400">delete</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <h3 className="text-lg font-semibold mb-3">Transactions</h3>
      <div className="space-y-2">
        {txns.length === 0 && (
          <div className="text-center py-12 text-gray-600">
            <p className="text-3xl mb-2">💰</p>
            <p>No transactions yet. Start tracking your money.</p>
          </div>
        )}
        {txns.map((t) => (
          <div key={t.id} className="bg-gray-900 rounded-lg p-3 border border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className={`w-2 h-2 rounded-full ${t.type === "income" ? "bg-green-400" : "bg-red-400"}`} />
              <div>
                <p className="text-sm font-medium">
                  {t.category}{t.description ? ` — ${t.description}` : ""}
                  {t.recurring && <span className="text-xs text-yellow-500 ml-2">recurring</span>}
                </p>
                <p className="text-xs text-gray-500">{t.date}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <p className={`text-sm font-mono font-medium ${t.type === "income" ? "text-green-400" : "text-red-400"}`}>
                {t.type === "income" ? "+" : "-"}{t.currency} {fmt(t.amount)}
              </p>
              <button onClick={() => deleteTx(t.id)} className="text-xs text-gray-600 hover:text-red-400">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
