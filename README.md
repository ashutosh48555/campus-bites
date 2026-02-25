# campus-bites

College shop pre-order and crowd management web app.

## Project Status

✅ **All issues resolved** - Project reviewed and tested on February 23, 2026
- Fixed template errors
- Added proper navigation for shop owners
- Configured static files properly
- Added .gitignore for version control

See [PROJECT_REVIEW.md](PROJECT_REVIEW.md) for detailed list of fixes.

## Quick start

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Start the server:
   ```
   python manage.py runserver
   ```

6. Access the application:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Setup Test Data

A database containing pre-generated test data is already included. You can log in using:

**Admin**
- `admin@campus.com` / `Admin@123`

**Shop Owners (Fully Populated Indian Menus)**
- The Indian Canteen: `canteen@campus.com` / `Owner@123`
- South Indian Express: `south@campus.com` / `Owner@123`
- Campus Maggie & Rolls: `maggie@campus.com` / `Owner@123`

**Student / Customer**
- `student@campus.com` / `Student@123`

See [ADMIN_SETUP_GUIDE.md](ADMIN_SETUP_GUIDE.md) for detailed instructions on creating new test shops, menu items, and users manually.

## Notes

- Tailwind is loaded via CDN in templates.
- SQLite is used for local development.
- Media files are stored in `media/` directory.
- Static files configured for both development and production.

