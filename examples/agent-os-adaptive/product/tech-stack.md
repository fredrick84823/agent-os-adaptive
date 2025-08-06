# Technical Stack

> Last Updated: 2025-08-06
> Version: 1.0.0

## Application Framework
- **Google ADK (Agent Development Kit)**: ^1.5.0
- **Python**: ^3.12

## Database System
- **BigQuery**: Google Cloud BigQuery with multi-project support
- **Service Account Authentication**: JSON credential-based authentication

## JavaScript Framework
- **N/A**: Pure Python backend system

## Import Strategy
- **Python Modules**: Standard Python import system with Poetry dependency management

## CSS Framework
- **N/A**: Backend system without web UI components

## UI Component Library
- **ADK Web GUI**: Built-in web interface for agent interactions
- **Plotly**: ^5.24.1 for data visualization and interactive charts

## Fonts Provider
- **N/A**: Backend system

## Icon Library
- **N/A**: Backend system

## Application Hosting
- **Vertex AI Agent Engine**: Primary deployment target for production
- **Cloud Run**: Planned deployment platform for scalable containerized hosting
- **Local Development**: Poetry-managed virtual environments

## Database Hosting
- **Google Cloud BigQuery**: Managed data warehouse service
- **Multi-Project Configuration**: Support for cross-project data federation

## Asset Hosting
- **Google Cloud Storage**: Artifact storage for CSV exports and visualizations
- **Vertex AI Extensions**: Code interpreter artifacts and execution results

## Deployment Solution
- **Docker**: Containerized deployments with Poetry wheel building
- **Cloud Run**: Serverless container platform (planned)
- **Vertex AI Agent Engine**: Managed AI agent hosting platform
- **GitHub**: Version control and CI/CD integration

## Code Repository URL
- **Repository**: https://github.com/google/adk-samples
- **Path**: /python/agents/data-science

## Core Dependencies

### AI & Machine Learning
- **google-cloud-aiplatform**: ^1.93.0 (with adk, agent-engines extras)
- **google-genai**: Vertex AI and Gemini integration
- **google-adk**: ^1.5.0 (Agent Development Kit framework)

### Data Processing & Analytics
- **pandas**: ^2.3.0 (DataFrame operations and data manipulation)
- **numpy**: ^2.3.1 (Numerical computing operations)
- **plotly**: ^5.24.1 (Interactive data visualization)
- **tabulate**: ^0.9.0 (Table formatting and display)

### Database & Query Processing
- **db-dtypes**: ^1.4.2 (BigQuery data type handling)
- **sqlglot**: ^26.10.1 (SQL parsing and optimization)
- **regex**: ^2024.11.6 (Advanced pattern matching for SQL processing)

### Configuration & Environment
- **python-dotenv**: ^1.0.1 (Environment variable management)
- **pydantic**: ^2.11.3 (Data validation and settings management)
- **immutabledict**: ^4.2.1 (Immutable dictionary structures)
- **absl-py**: ^2.2.2 (Google command-line flag processing)

### Development & Testing
- **pytest**: ^8.3.5 (Testing framework)
- **pytest-asyncio**: ^0.26.0 (Async testing support)
- **google-adk[eval]**: ^1.5.0 (Evaluation and testing utilities)

## Architecture Patterns

### Multi-Agent System
- **Root Agent**: Central orchestrator for task delegation
- **Specialized Sub-Agents**: Database, Analytics, and BQML agents
- **Tool Integration**: Agent tools for specific functionality

### Natural Language Processing
- **CHASE-SQL**: Advanced NL2SQL conversion system
- **RAG Integration**: Retrieval-augmented generation for BQML documentation
- **Prompt Engineering**: Structured prompt templates for agent behavior

### Cloud-Native Integration
- **Vertex AI Integration**: Native Google Cloud AI platform support
- **Service Account Authentication**: Enterprise-ready security model
- **Multi-Project Support**: Cross-project BigQuery federation

### Data Pipeline Architecture
- **Query Generation**: NL2SQL with validation and post-processing
- **Result Processing**: Automated data analysis and visualization
- **Export Capabilities**: CSV generation with artifact management
- **Session State**: Persistent conversation context and memory

## Security & Authentication
- **Service Account**: JSON-based Google Cloud authentication
- **IAM Integration**: Role-based access control for BigQuery resources
- **Environment Variables**: Secure credential and configuration management
- **Query Validation**: SQL injection prevention and query optimization

## Performance & Scalability
- **Query Limits**: Configurable row limits (default: 80 rows) for performance
- **Async Operations**: Asynchronous processing for improved responsiveness
- **Caching Strategy**: Session state management for conversation context
- **Resource Management**: Memory-efficient data processing with pandas

## Monitoring & Observability
- **Comprehensive Logging**: Structured logging with pytest integration
- **Evaluation Framework**: Built-in testing and evaluation capabilities
- **Error Handling**: Robust error management and user feedback
- **Performance Metrics**: Query execution timing and resource usage tracking