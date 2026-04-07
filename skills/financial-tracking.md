# Skill: Financial Tracking

## When to use
When processing financial data — adding transactions, categorizing expenses, generating summaries.

## Procedures

### Adding a transaction
1. Parse the input for: type (income/expense), amount, category, date, description
2. If type is unclear, ask
3. If category is ambiguous, pick the closest match and mention it
4. Default currency to LKR unless specified
5. If it sounds recurring (salary, rent, subscription), flag it as recurring

### Categorizing automatically
Use these keywords to auto-categorize:
- **rent**: "rent", "house", "apartment"
- **food**: "lunch", "dinner", "groceries", "restaurant", "uber eats"
- **transport**: "fuel", "petrol", "uber", "bus", "train"
- **utilities**: "electricity", "water", "internet", "phone"
- **subscriptions**: "netflix", "spotify", "github", "cloud"
- **salary**: "salary", "paycheck", "wages"
- **freelance**: "freelance", "contract", "gig", "client payment"

### Monthly summary format
```
📊 Financial Summary — [Month Year]
Income:  LKR XX,XXX
Expense: LKR XX,XXX
Net:     LKR XX,XXX (XX% savings rate)

Top expenses:
1. Category — LKR X,XXX
2. Category — LKR X,XXX
3. Category — LKR X,XXX

Loans:
- Loan name: LKR X,XXX remaining (LKR X,XXX/month)
```
