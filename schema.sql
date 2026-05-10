-- schema.sql
-- Defines all 4 tables for the patent database
-- Run this first before loading any data
-- Drop tables if they exist so we can re-run cleanly
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;
-- TABLE 1: patents
-- Stores core patent information
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    filing_date TEXT,
    year INTEGER
);
-- TABLE 2: inventors
-- Stores the people who invented the patents
CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT
);
-- TABLE 3: companies
-- Stores the companies that own the patents
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT
);
-- TABLE 4: relationships
-- Links patents to their inventors and companies
CREATE TABLE relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT,
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
-- Indexes to make queries run faster
CREATE INDEX idx_rel_patent ON relationships(patent_id);
CREATE INDEX idx_rel_inventor ON relationships(inventor_id);
CREATE INDEX idx_rel_company ON relationships(company_id);
CREATE INDEX idx_patent_year ON patents(year);