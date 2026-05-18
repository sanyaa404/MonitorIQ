SELECT 'CREATE DATABASE monitoring'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'monitoring')\gexec
