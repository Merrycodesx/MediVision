# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- JWT-based authentication system with token obtain and refresh endpoints (`/api/auth/token/`, `/api/auth/token/refresh/`)
- User registration API (`/api/auth/register/`)
- Patient CRUD operations with permission guards:
  - List and create patients (`/api/patients/`)
  - Retrieve, update, and delete individual patients (`/api/patients/<id>/`)
- Basic test API endpoint (`/api/test/`)
- Consolidated requirements.txt with all pinned dependencies
- Dockerfile for containerized backend deployment
- Comprehensive README.md with local setup instructions

### Changed
- Consolidated all Python dependencies into a single `requirements.txt` file in the root directory
- Updated project structure documentation

### Fixed
- Resolved merge conflicts and restored project state after git pull issues