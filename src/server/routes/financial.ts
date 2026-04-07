import { Router } from "express";
import {
  addTransaction,
  getTransactions,
  deleteTransaction,
  addLoan,
  getLoans,
  updateLoan,
  deleteLoan,
  getFinancialSummary,
} from "../services/financial-store.js";

const router = Router();

router.get("/status", async (_req, res) => {
  const summary = await getFinancialSummary();
  res.json({ status: "ok", faculty: "financial", ...summary });
});

router.get("/summary", async (req, res) => {
  try {
    const month = req.query.month as string | undefined;
    const summary = await getFinancialSummary(month);
    res.json(summary);
  } catch {
    res.status(500).json({ error: "Failed to get summary" });
  }
});

router.get("/transactions", async (req, res) => {
  try {
    const { from, to, type, limit } = req.query;
    const data = await getTransactions({
      from: from as string,
      to: to as string,
      type: type as string,
      limit: limit ? parseInt(limit as string) : undefined,
    });
    res.json(data);
  } catch {
    res.status(500).json({ error: "Failed to get transactions" });
  }
});

router.post("/transactions", async (req, res) => {
  try {
    const { type, category, amount, currency, description, date, recurring, recurringPeriod } = req.body;
    if (!type || !category || !amount || !date) {
      res.status(400).json({ error: "type, category, amount, and date are required" });
      return;
    }
    const tx = await addTransaction({
      type,
      category,
      amount: parseFloat(amount),
      currency,
      description,
      date,
      recurring,
      recurringPeriod,
    });
    res.status(201).json(tx);
  } catch {
    res.status(500).json({ error: "Failed to add transaction" });
  }
});

router.delete("/transactions/:id", async (req, res) => {
  try {
    await deleteTransaction(parseInt(req.params.id));
    res.json({ deleted: true });
  } catch {
    res.status(500).json({ error: "Failed to delete transaction" });
  }
});

router.get("/loans", async (_req, res) => {
  try {
    const data = await getLoans();
    res.json(data);
  } catch {
    res.status(500).json({ error: "Failed to get loans" });
  }
});

router.post("/loans", async (req, res) => {
  try {
    const { name, totalAmount, remainingAmount, monthlyPayment, interestRate, dueDate } = req.body;
    if (!name || !totalAmount) {
      res.status(400).json({ error: "name and totalAmount are required" });
      return;
    }
    const loan = await addLoan({
      name,
      totalAmount: parseFloat(totalAmount),
      remainingAmount: parseFloat(remainingAmount || totalAmount),
      monthlyPayment: monthlyPayment ? parseFloat(monthlyPayment) : undefined,
      interestRate: interestRate ? parseFloat(interestRate) : undefined,
      dueDate,
    });
    res.status(201).json(loan);
  } catch {
    res.status(500).json({ error: "Failed to add loan" });
  }
});

router.put("/loans/:id", async (req, res) => {
  try {
    const updated = await updateLoan(parseInt(req.params.id), req.body);
    res.json(updated[0]);
  } catch {
    res.status(500).json({ error: "Failed to update loan" });
  }
});

router.delete("/loans/:id", async (req, res) => {
  try {
    await deleteLoan(parseInt(req.params.id));
    res.json({ deleted: true });
  } catch {
    res.status(500).json({ error: "Failed to delete loan" });
  }
});

export default router;
