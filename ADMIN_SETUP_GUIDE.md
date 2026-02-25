# Admin Panel Setup Guide for campus-bites

## Step-by-Step Instructions to Create Test Data

### 1. Login to Admin Panel
- URL: `http://127.0.0.1:8000/admin/`
- Username: `admin`
- Password: `Admin@123`

---

## Option A: Use Pre-Generated Test Users

A script has been run to pre-generate test users for you. Use these credentials to test the application immediately:

1. **Admin User**
   - Email: `admin@campus.com`
   - Password: `Admin@123`

2. **Shop Owners (3 fully-populated shops)**
   - **Campus Central Cafe:** `cafe@campus.com` / `Owner@123`
   - **The Spicy Wok:** `wok@campus.com` / `Owner@123`
   - **Healthy Greens:** `healthy@campus.com` / `Owner@123`

3. **College Student**
   - Email: `student@campus.com`
   - Password: `Student@123`

If you would rather create users manually, follow Option B below.

---

## Option B: Create a Shop Owner User (Manual)

### Step 1: Create a User
1. Go to **Users** section
2. Click **Add User**
3. Enter:
   - **Username**: `shopowner1@campus.com` (Use an email format)
   - **Password**: (set any password)
   - **Confirm password**: (same as above)
4. Click **Save**
5. On the next page, fill optional fields like First name, Last name, Email
6. Click **Save and continue editing**

### Step 2: Create a Profile for this User
1. Go to **Profiles** section
2. Click **Add Profile**
3. Fill:
   - **User**: select `shopowner1` (the user you just created)
   - **Role**: select `shop_owner` from dropdown
   - **College ID**: leave blank (not needed for shop owners)
   - **Phone number**: (optional)
4. Click **Save**

### Step 3: Create a Shop
1. Go to **Shops** section
2. Click **Add Shop**
3. Fill:
   - **Name**: `Campus Cafe` (or any shop name)
   - **Description**: `Fresh coffee and snacks` (optional)
   - **Address**: `Building A, Ground Floor` (optional but recommended)
   - **Owner**: select `shopowner1` (the shop owner user)
   - **Opening time**: `09:00:00` (9 AM)
   - **Closing time**: `18:00:00` (6 PM)
   - **Max orders per slot**: `5` (max orders in a 15-min slot)
4. Click **Save**

### Step 4: Create Menu Categories (Optional but Recommended)
1. Go to **Categories** section
2. Click **Add Category**
3. Fill:
   - **Shop**: select `Campus Cafe`
   - **Name**: `Beverages` (or `Snacks`, `Meals`, etc.)
4. Click **Save**
5. Repeat for other categories

### Step 5: Create Menu Items
1. Go to **Menu Items** section
2. Click **Add Menu Item**
3. Fill:
   - **Shop**: select `Campus Cafe`
   - **Category**: select `Beverages` (the category you created)
   - **Name**: `Coffee` (or any item name)
   - **Description**: `Hot espresso coffee` (optional)
   - **Price**: `100.00`
   - **Is available**: ✓ (checked)
   - **Preparation time minutes**: `5`
4. Click **Save**
5. Repeat for more items like:
   - Tea - 80.00
   - Sandwich - 150.00
   - Cookies - 50.00

---

## Step 6: Test the Shop Owner Flow

1. **Log out** from admin
2. Go to home page: `http://127.0.0.1:8000/`
3. You should see **Campus Cafe** on the shop list
4. **Log in** as `shopowner1` (the shop owner user you created)
5. Go to owner dashboard: `http://127.0.0.1:8000/owner/dashboard/`
   - You will see today's orders (none yet)

---

## Step 7: Test Complete Flow as a College User

1. **Log out** from shop owner account
2. Go to register: `http://127.0.0.1:8000/accounts/login/`
3. Log in as the pre-generated college user:
   - **Email**: `student@campus.com`
   - **Password**: `Student@123`
   *(Or you can register a new one manually)*
4. You will be logged in automatically
5. Click on **Campus Cafe** to view menu
6. Add items to cart
7. Click **Checkout**
   - Select a pickup time (15 mins from now or later)
   - Select payment method (Cash or Online)
   - Click **Place order**
8. Go to **My Orders** to see your order with:
   - Shop name
   - Token number (auto-generated)
   - Pickup time
   - Status badge (yellow = pending)

---

## Step 8: Test Shop Owner Receives Order

1. **Log out** 
2. **Log in as shop owner** (`shopowner1`)
3. Go to owner dashboard
4. You will see the order from the college user with:
   - Token number
   - Pickup time
   - Current status dropdown
5. Click **Update** to change status:
   - `pending` → `preparing` → `ready` → `collected`

---

## Step 9: Customer Sees Live Status

1. **Log out** from shop owner
2. **Log in as college user** (john@college.com)
3. Go to **My Orders**
4. See the order with the updated status in real-time

---

## Summary of What Each Section Does

| Section | Purpose |
|---------|---------|
| **Users** | Create login accounts |
| **Profiles** | Assign role (college_user or shop_owner) |
---

## Step 9: Shop Owner Menu Management (NEW!)

### Shop owners can now manage their own menu without admin access!

1. **Log in as shop owner** (e.g., `shopowner1`)
2. Go to **Owner Dashboard**: `http://127.0.0.1:8000/owner/dashboard/`
3. You'll see three quick action cards:
   - **Manage Menu** - Add/edit menu items and categories
   - **Shop Settings** - Update shop details (hours, capacity, address)
   - **Today's Orders** - Count of orders

### Managing Categories

1. Click **Manage Menu** button
2. Click **+ Add Category**
3. Enter category name (e.g., "Beverages", "Snacks", "Meals")
4. Click **Save Category**
5. Category appears in the categories section
6. You can **Edit** or **Delete** categories

### Managing Menu Items

1. Click **Manage Menu** button
2. Click **+ Add Menu Item**
3. Fill in the form:
   - **Item Name**: e.g., "Cappuccino"
   - **Category**: Select from dropdown (create categories first!)
   - **Description**: Optional details about the item
   - **Price**: In rupees (e.g., 100.00)
   - **Prep Time**: Minutes needed to prepare (e.g., 5)
   - **Item Image**: Upload a photo (optional but recommended)
   - **Available**: Check this box if item is currently available
4. Click **Save Menu Item**
5. Item appears in the menu items table

### Quick Actions for Menu Items

From the **Manage Menu** page, you can:

- **Mark Out/Mark In**: Quickly mark items as out of stock or available
- **Edit**: Update item details, price, or image
- **Delete**: Remove item permanently (with confirmation)

### Updating Shop Settings

1. Click **Shop Settings** from the dashboard
2. Update:
   - Shop name
   - Description
   - Address
   - Opening/closing times
   - Max orders per 15-minute slot (crowd control)
3. Click **Save Settings**

### Image Uploads

- Supported formats: JPG, PNG, GIF
- Images are stored in `/media/menu_items/`
- Images appear on the shop detail page for customers
- Recommended size: 800x600 pixels or similar aspect ratio

---

## Summary of What Each Section Does

| Section | Purpose |
|---------|---------|
| **Users** | Create login accounts |
| **Profiles** | Assign role (college_user or shop_owner) |
| **Shops** | Create a shop with hours and capacity |
| **Categories** | Organize menu items (Coffee, Snacks, etc.) |
| **Menu Items** | Add individual food/drink items with price |
| **Orders** | View all orders (read-only for shop owner) |
| **Payments** | Track payment status for each order |

---

## Quick Checklist

- [ ] Create shop owner user
- [ ] Create shop owner profile with role=shop_owner
- [ ] Create a shop linked to shop owner
- [ ] Create menu categories (Beverages, Snacks, etc.)
- [ ] Create menu items (Coffee, Tea, Sandwich, etc.)
- [ ] Create college user account
- [ ] Add items to cart and place order
- [ ] View order in shop owner dashboard
- [ ] Update order status
- [ ] See live status as college user

---

## URLs to Remember

| URL | Purpose |
|-----|---------|
| `http://127.0.0.1:8000/admin/` | Admin panel (create data) |
| `http://127.0.0.1:8000/` | Home (shop list) |
| `http://127.0.0.1:8000/accounts/login/` | Login page |
| `http://127.0.0.1:8000/accounts/register/` | Register college user |
| `http://127.0.0.1:8000/owner/dashboard/` | Shop owner dashboard |
| `http://127.0.0.1:8000/owner/menu/` | Shop owner menu management |
| `http://127.0.0.1:8000/owner/settings/` | Shop owner settings |
| `http://127.0.0.1:8000/orders/my/` | My orders (college user) |

