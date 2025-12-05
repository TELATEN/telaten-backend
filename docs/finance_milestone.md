# 💰 Finance Module

The `app/modules/finance` directory provides **financial tracking**, including transaction recording, summaries, and category management.

---

## 🧩 Models (`models.py`)

### **`TransactionCategory`**

Represents predefined or custom categories for classifying transactions.

* **Fields:**
  `name`, `type` (income/expense), `icon`, `is_default`,
  `business_id` *(nullable for system defaults)*

---

### **`Transaction`**

Stores individual financial records.

* **Fields:**

  * `amount` — numeric(12, 2)
  * `type` — income or expense
  * `category`, `category_id`
  * `payment_method` — cash, transfer, etc.
  * `transaction_date`, `description`
  * `business_id` — links the transaction to the business profile

---

## ⚙️ Service (`service.py`)

### **`FinanceService`**

* **`create_transaction`**
  Records a transaction.
  **Integration:** awards gamification points (e.g., 5 points) for consistent financial tracking.

* **`get_transactions`**
  Returns paginated transaction records with optional date filtering.

* **`get_summary`**
  Produces financial summaries for a specified timeframe (day, week, month, year), including:

  * income vs. expense
  * net profit
  * breakdown by category

* **Category Management**
  Create, list, and delete custom transaction categories.

---

# 🎯 Milestone Module

The `app/modules/milestone` directory manages **business milestones**, actionable steps, and task progress.

---

## 🧩 Models (`models.py`)

### **`Milestone`**

Represents a major business goal or growth phase.

* **Fields:**

  * `title`, `description`
  * `status` — pending, in_progress, completed
  * `order`, `level`, `reward_points`
  * `started_at`, `completed_at`
  * `is_generated` — indicates whether it was created by the AI
  * `tasks` — list of sub-tasks

---

### **`MilestoneTask`**

A sub-task inside a milestone.

* **Fields:** `title`, `is_completed`, `reward_points`

---

## ⚙️ Service (`service.py`)

### **`MilestoneService`**

* **`start_milestone`**
  Sets a milestone status to *in_progress*.

* **`complete_task`**
  Marks a task as completed.
  **Logic:**

  * awards points for task completion
  * **auto-completion**: if all tasks are completed, the milestone is marked as finished and bonus points are granted

* **AI Integration** — `_check_and_trigger_generation`

  * Monitors the set of active milestones
  * When **all** milestones are completed, it triggers the **auto-generate workflow**
  * Uses AI memory and recent chat context to create the next logical set of milestones

---
