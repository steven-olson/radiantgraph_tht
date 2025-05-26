-- Database initialization script
-- This file is optional and runs when the database container starts for the first time

-- Create any additional database objects if needed
-- For now, the application handles table creation through SQLAlchemy

-- You can add initial data here if needed:
-- INSERT INTO location (location_type, address_line_1, address_line_2, city, state, zip_code)
-- VALUES ('store', '123 Main St', '', 'Example City', 'CA', '12345');

-- Grant permissions if needed
GRANT ALL PRIVILEGES ON DATABASE radiant_graph TO postgres;