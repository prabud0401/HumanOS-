import { getDB } from "../db/index.js";
import { transactions, loans } from "../db/schema.js";
import { eq, desc, and, gte, lte } from "drizzle-orm";

export interface TransactionInput {
  type: "income" | "expense";
  category: string;
  amount: number;
  currency?: string;
  description?: string;
  date: string;
  recurring?: boolean;
  recurringPeriod?: string;
}

export async function addTransaction(input: TransactionInput) {
  const db = getDB();
  const result = await db
    .insert(transactions)
    .values({
      type: input.type,
      category: input.category,
      amount: input.amount,
      currency: input.currency || "LKR",
      description: input.description || "",
      date: input.date,
      recurring: input.recurring || false,
      recurringPeriod: input.recurringPeriod || null,
      createdAt: new Date().toISOString(),
    })
    .returning();
  return result[0];
}

export async function getTransactions(options?: {
  from?: string;
  to?: string;
  type?: string;
  limit?: number;
}) {
  const db = getDB();
  const conditions = [];

  if (options?.from) conditions.push(gte(transactions.date, options.from));
  if (options?.to) conditions.push(lte(transactions.date, options.to));
  if (options?.type) conditions.push(eq(transactions.type, options.type));

  const query = db
    .select()
    .from(transactions)
    .orderBy(desc(transactions.date))
    .limit(options?.limit || 100);

  if (conditions.length > 0) {
    return query.where(and(...conditions));
  }
  return query;
}

export async function deleteTransaction(id: number) {
  const db = getDB();
  return db.delete(transactions).where(eq(transactions.id, id));
}

export async function addLoan(input: {
  name: string;
  totalAmount: number;
  remainingAmount: number;
  monthlyPayment?: number;
  interestRate?: number;
  dueDate?: string;
}) {
  const db = getDB();
  const result = await db
    .insert(loans)
    .values({
      name: input.name,
      totalAmount: input.totalAmount,
      remainingAmount: input.remainingAmount,
      monthlyPayment: input.monthlyPayment || 0,
      interestRate: input.interestRate || 0,
      dueDate: input.dueDate || null,
      status: "active",
      createdAt: new Date().toISOString(),
    })
    .returning();
  return result[0];
}

export async function getLoans() {
  const db = getDB();
  return db.select().from(loans).orderBy(desc(loans.createdAt));
}

export async function updateLoan(
  id: number,
  updates: Partial<{
    remainingAmount: number;
    monthlyPayment: number;
    status: string;
  }>
) {
  const db = getDB();
  return db.update(loans).set(updates).where(eq(loans.id, id)).returning();
}

export async function deleteLoan(id: number) {
  const db = getDB();
  return db.delete(loans).where(eq(loans.id, id));
}

export async function getFinancialSummary(month?: string) {
  const db = getDB();
  const all = await db.select().from(transactions);

  const filtered = month
    ? all.filter((t) => t.date.startsWith(month))
    : all;

  const totalIncome = filtered
    .filter((t) => t.type === "income")
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpense = filtered
    .filter((t) => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  const byCategory: Record<string, number> = {};
  for (const t of filtered) {
    byCategory[t.category] = (byCategory[t.category] || 0) + t.amount;
  }

  const allLoans = await db.select().from(loans);
  const totalDebt = allLoans
    .filter((l) => l.status === "active")
    .reduce((sum, l) => sum + l.remainingAmount, 0);

  const monthlyLoanPayments = allLoans
    .filter((l) => l.status === "active")
    .reduce((sum, l) => sum + (l.monthlyPayment || 0), 0);

  return {
    totalIncome,
    totalExpense,
    net: totalIncome - totalExpense,
    savingsRate: totalIncome > 0 ? ((totalIncome - totalExpense) / totalIncome) * 100 : 0,
    byCategory,
    totalDebt,
    monthlyLoanPayments,
    transactionCount: filtered.length,
  };
}
