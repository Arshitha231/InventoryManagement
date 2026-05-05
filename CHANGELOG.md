# Changelog

## [1.0.0] - 2026-05-05

### Added
- Complete product CRUD operations (add, view, update, delete)
- Stock control: restock and sale recording with quantity tracking
- Price management for individual products
- Supplier management (add and list suppliers)
- Low stock alerts with configurable per-product thresholds
- Inventory reporting with category breakdowns
- Audit log tracking all inventory changes
- CSV export functionality
- Product search by name, category, or ID
- Formatted table output using tabulate
- Colored terminal output using colorama
- Environment variable configuration via python-dotenv
- Comprehensive unit tests with mock database
- Database schema with proper foreign keys and indexes
- Seed data for easy development setup

### Fixed
- Update Stock feature was empty stub — now fully implemented
- Hardcoded database credentials — moved to .env file
- No error handling — added try/except for all database operations
- No input validation — added validators for int, float, and string inputs
- Raw tuple output — replaced with formatted table display

### Security
- Database credentials moved from source code to .env file
- Added .env to .gitignore to prevent credential leaks
- Parameterized queries prevent SQL injection
