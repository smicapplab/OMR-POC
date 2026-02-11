---

# ⚙️ Technology Stack

## Backend API
- NestJS
- Drizzle ORM
- SQLite (better-sqlite3)
- JWT Authentication
- bcrypt password hashing

## OMR Engine
- Python
- OpenCV
- Deskew and normalization
- Bubble grid overlay validation
- Fill ratio and contour-based scoring
- Debug heatmaps

## Frontend
- Next.js
- React

---

# 🔐 Authentication

Role-based authentication with JWT.

Supported roles:
- `admin`
- `user`

Seeded demo accounts:

| Email | Password | Role |
|-------|----------|------|
| storrefranca@gmail.com | password | admin |
| aldrich.abrogena@dice205.com | password | user |

Passwords are hashed using bcrypt.

---

# 🗄 Database

- SQLite (`omr.db`)
- Shared between Python OMR processor and NestJS backend
- WAL mode enabled for multi-process safety
- Foreign keys enabled

Seed tracking is handled via a `seed_history` table to prevent duplicate seed execution.

---

# 🚀 Setup Instructions

## 1️⃣ Install SQLite

Make sure SQLite is installed on your machine.

### macOS (Homebrew)

```bash
brew install sqlite
```

Verify installation:

```bash
sqlite3 --version
```

---

## 2️⃣ Create OMR Database

From the project root:

```bash
touch omr.db
```

This creates the shared SQLite database used by both:
- Python OMR engine
- NestJS backend

Ensure your `.env` contains:

```bash
OMR_DB_PATH=../omr.db
```

---

## 3️⃣ Install Backend Dependencies

```bash
cd be-omr-demo
npm install
```

---

## 4️⃣ Run Drizzle Schema Push / Migration

From `be-omr-demo`:

```bash
npx drizzle-kit push
```

This will:
- Create `users` table
- Create `seed_history` table
- Apply schema to `omr.db`

---

## 5️⃣ Run Seeds

```bash
npx ts-node seeds/seed-users.ts
```

This will insert:
- Admin user
- Regular user

Seed execution is tracked in `seed_history` to prevent duplicates.

---

## 6️⃣ Start Backend (Development Mode)

```bash
npm run start:dev
```

---

The system is now ready for authentication and OMR integration.