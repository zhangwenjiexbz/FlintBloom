# Changelog

All notable changes to FlintBloom will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- React frontend with trace visualization
- Checkpoint replay functionality
- Advanced cost optimization suggestions
- Prompt version management
- Team collaboration features
- Export/import functionality
- Performance profiling tools
- Custom metrics and alerts

## [0.1.0] - 2024-01-XX

### Added
- Initial release of FlintBloom
- Core backend architecture with FastAPI
- Multi-database support (MySQL, PostgreSQL, SQLite)
- Offline checkpoint analysis module
  - Thread listing and filtering
  - Checkpoint parsing and analysis
  - Trace graph generation
  - Token usage and cost calculation
  - Performance metrics
  - Checkpoint comparison
- Real-time tracking module
  - Custom LangChain callback handler
  - WebSocket streaming
  - Event buffering and replay
  - Real-time metrics
- Database adapters with unified interface
- RESTful API with OpenAPI documentation
- Docker Compose setup for easy deployment
- Comprehensive documentation
- Example scripts and usage guides
- Basic frontend structure (placeholder)

### Features
- ✅ Read from LangGraph checkpoint tables
- ✅ Zero runtime overhead for offline analysis
- ✅ Real-time event streaming via WebSocket
- ✅ Token usage and cost tracking
- ✅ Performance metrics and bottleneck detection
- ✅ Thread timeline visualization
- ✅ Checkpoint comparison
- ✅ Multi-database support
- ✅ Docker deployment
- ✅ RESTful API with Swagger docs

### Technical Details
- Python 3.11+
- FastAPI 0.115.0
- SQLAlchemy 2.0.35
- LangChain 1.0.0
- LangGraph 1.0.0
- React 18.2.0 (frontend)
- TypeScript 5.3.3 (frontend)

[Unreleased]: https://github.com/zhangwenjiexbz/FlintBloom/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/zhangwenjiexbz/FlintBloom/releases/tag/v0.1.0
