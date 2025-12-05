# 🔐 Authentication Module

The `app/modules/auth` directory manages **user registration**, **authentication**, and **role control**.

---

## 🧩 Models (`models.py`)

### **User**

Represents the primary user entity.

* `id`: UUID
* `email`: Unique identifier for login
* `name`: Full name
* `hashed_password`: Securely hashed password
* `role`: User role — default `"user"`, optional `"admin"`
* `created_at`, `updated_at`: Automatic timestamps

### **DTOs**

Data Transfer Objects for clean input/output schemas.

* **`UserCreate`** — payload for registering a new user
* **`UserLogin`** — payload for login
* **`UserRead`** — response model for returning user data

---

## ⚙️ Service (`service.py`)

### **`AuthService`**

* **`register_user`**:
  Creates a new account if the email is not already used.

* **`authenticate_user`**:
  Validates user credentials, issues an access token, and sets a secure HTTP-only refresh token cookie.

* **`refresh_access_token`**:
  Validates the refresh token and generates a new access token.

---

# 🏢 Business Module

The `app/modules/business` directory handles **business profiles**, **gamification levels**, and the **AI onboarding workflow**.

---

## 🧩 Models (`models.py`)

### **BusinessProfile**

Stores all business-related data for each user.

**Key fields:**

* `business_name`, `business_category`, `business_description`
* `business_stage`, `target_market`, `primary_goal`
* `address`: Structured JSON address
* `total_points`: Gamification score
* `ai_context`: Memory storage for the AI agent (state, focus, risks)
* `level_id`: Foreign key referencing `BusinessLevel`

---

### **BusinessLevel**

Represents the gamification tiers for businesses.

**Fields:**
`name`, `required_points`, `order`, `icon`

---

## ⚙️ Service (`service.py`)

### **`BusinessService`**

* **`get_profile`**:
  Retrieves the user's business profile along with current level information.

* **`create_profile`**:
  Creates a new `BusinessProfile` for the authenticated user.

* **`update_profile`**:
  Modifies business details.

* **`add_points`**:
  Increases gamification points and updates level when required.

### **AI Integration**

* **`generate_milestones_stream`**:
  Invokes the AI onboarding workflow to generate milestones tailored to the business data.
  Returns updates via **Server-Sent Events (SSE)**.

---

# 🔧 Admin Module

The `app/modules/business/admin_routes.py` provides restricted endpoints for system administrators.

## ⚙️ Capabilities

* **`get_all_businesses`**: View all registered business profiles.
* **`delete_business`**: Hard delete a business profile (and associated data).

---
