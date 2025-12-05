# 🏆 Gamification Module

The `app/modules/gamification` directory manages **achievements**, **business levels**, and the **leaderboard system** to keep users engaged and motivated.

---

## 🧩 Models (`models.py`)

### **`Achievement`**

Represents a predefined badge or milestone that users can unlock.

* **Fields:**
  `title`, `description`, `required_points`, `badge_icon`

---

### **`UserAchievement`**

A mapping table that records which achievements a user has unlocked.

* **Fields:**
  `user_id`, `achievement_id`, `unlocked_at`

---

### **`LeaderboardEntry`**

DTO used to return leaderboard data.

* **Fields:**
  `rank`, `business_name`, `total_points`,
  `level_name`, `user_name`, `achievements_count`

---

## ⚙️ Service (`service.py`)

### **`GamificationService`**

* **`process_gamification`**
  Evaluates whether the user qualifies for a **level upgrade** or any **new achievements** after points are added.
  Returns a list of newly unlocked titles.

* **`check_and_update_level`**
  Updates a business’s level based on accumulated points.

* **`get_leaderboard`**
  Returns the **top-ranked businesses** sorted by total points, optionally including the current user's own rank.

---

# 🔧 Gamification Admin Module

The `app/modules/gamification/admin_routes.py` handles configuration of game elements.

## ⚙️ Capabilities

* **`create_achievement`**: Add new unlockable achievements to the system.
* **`create_level`**: Define new business levels/tiers.

---

# 💬 Chat Module

The `app/modules/chat` directory powers AI-driven conversations enriched with business context and memory.

---

## 🧩 Models (`models.py`)

### **`ChatSession`**

Groups messages into dedicated conversation threads.

* **Fields:**
  `title`, `business_id`, `created_at`

---

### **`ChatMessage`**

Represents an individual message in a session.

* **Fields:**
  `role` (user / assistant),
  `content`,
  `session_id`

---

## ⚙️ Service (`service.py`)

### **`ChatService`**

* **`get_business_sessions`**
  Lists all chat sessions belonging to a specific business.

* **`get_session_messages`**
  Returns the messages within a given session.

* **`stream_chat_completion`**
  Handles real-time AI chat with full context injection.
  **Core Logic:**

  * Validates business ownership
  * Creates a new session if no session ID is provided
  * Injects business context (Business Name, Stage, User Name) into the system prompt
  * Streams model responses and tool execution updates using `llama_index` workflows via **SSE**

---
