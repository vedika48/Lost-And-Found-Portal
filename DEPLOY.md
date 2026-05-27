# Deploying CampusFind to Render

This guide explains how to deploy the CampusFind platform (FastAPI backend + HTML frontend) to **Render.com**.

## Prerequisite

1. Push your project code to a remote GitHub or GitLab repository.
2. Sign up/Log in to [Render.com](https://render.com).

---

## Deployment Steps

There are two ways to deploy on Render: **Blueprint** (recommended) or **Manual Setup**.

### Option A: Deploy using Blueprint (Recommended)

Render can read the `render.yaml` file in the root of your repository to automatically configure the service.

1. Go to your **Render Dashboard**.
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository containing the project.
4. Render will detect the `render.yaml` file and show the configuration:
   - **Service Name**: `campusfind`
   - **Runtime**: `Python`
5. Click **Apply**. Render will automatically build and deploy your app!

---

### Option B: Manual Setup

If you prefer to configure the Web Service manually via the Render UI:

1. Click **New +** on the Render Dashboard and choose **Web Service**.
2. Connect your GitHub repository.
3. Configure the following settings:
   - **Name**: `campusfind`
   - **Language/Runtime**: `Python 3`
   - **Branch**: `main` (or your default branch)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Select **Free** (or a paid instance if you want persistent storage).
4. Expand the **Advanced** section and add the following Environment Variable:
   - **Key**: `DATABASE_PATH`
   - **Value**: `campusfind.db`
5. Click **Create Web Service**.

---

## SQLite Database Persistence (Important)

Because SQLite stores data in a local file, we must consider how files are managed on Render:

### 1. Free Tier (Temporary Storage)
On Render's Free tier, the filesystem is ephemeral. Whenever your web service restarts or rebuilds (which happens at least once a day, and on every deploy), the `campusfind.db` file will be reset to its initial state.
* This is fine for testing and demoing, but data won't persist permanently.

### 2. Paid Tier (Persistent Storage via Disks)
To keep the SQLite database permanent across server restarts and new deploys:
1. Upgrade the instance type to **Starter** ($7/month).
2. Attach a **Disk** to the service:
   - **Disk Name**: `campusfind-data`
   - **Mount Path**: `/data`
   - **Size**: `1 GB` (or more)
3. Change the environment variable `DATABASE_PATH` value to `/data/campusfind.db`.
4. If using Option A (Blueprints), uncomment the `disk:` configuration section in `render.yaml` and update the `DATABASE_PATH` env var value to `/data/campusfind.db`.
