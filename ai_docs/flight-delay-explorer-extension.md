# Flight Delay Explorer Extension

Extension of the existing Flight Delay Explorer CLI tool to provide comprehensive historical trend analysis and route reliability scoring using the AviationStack API.

## Command Structure

The project will be restructured from a single-command tool into a multi-command suite with three main command groups:

- `flights` - Current flight data (enhanced version of existing functionality)
- `seasonal` - Seasonal delay pattern analysis
- `degraded` - Performance degradation detection

## Technical Architecture

### API Integration

- Primary use of AviationStack `/v1/flights` endpoint for flight data
- Additional endpoints for enhanced metadata
- Historical data collection and local storage for trend analysis

### Implementation Phases

1. Phase 1: Extend existing tool to support new command structure and data storage
2. Phase 2: Implement historical data collection capabilities
3. Phase 3: Build seasonal analysis functionality
4. Phase 4: Add performance degradation detection and alerting

## Learning Objectives

- Advanced CLI design patterns using Typer command groups
- Time-series data analysis with pandas
- Statistical analysis and trend detection
- SQLite database design and optimization
- Historical data management and caching strategies

Extension of the existing Flight Delay Explorer CLI tool to provide comprehensive historical trend analysis and route reliability scoring using the AviationStack API.

## Command Structure

The project will be restructured from a single-command tool into a multi-command suite with three main command groups:

### Command Groups

1. `flights` - Current flight data (enhanced version of existing functionality)
2. `seasonal` - Seasonal delay pattern analysis
3. `degraded` - Performance degradation detection

## Detailed Command Specifications

### flights Command Group (Enhanced Current Functionality)

Purpose: Real-time and specific-date flight data with advanced filtering capabilities

Supported Data Filters:

- `--date YYYY-MM-DD` - Fetches flight data for the specified date (existing core functionality)
- `--route "CODE->CODE"` - Filters to flights between specific departure and arrival airports (e.g., "DFW->LAX")
- `--airline CODE` - Filters to flights operated by a specific airline using IATA/ICAO codes (e.g., "AA", "UA")
- `--airport CODE` - Shows all flights departing from or arriving at the specified airport code
- `--departures-only` - When used with --airport, shows only outbound flights from that airport
- `--arrivals-only` - When used with --airport, shows only inbound flights to that airport
- `--min-delay MINUTES` - Filters to flights with delays equal to or greater than the specified minutes
- `--status STATUS` - Filters by flight status: "scheduled", "active", "landed", "cancelled", "incident", "diverted"
- `--export FORMAT` - Exports filtered results to file format: "csv", "json", or "xlsx"
- `--limit NUMBER` - Limits output to the specified number of flights (useful for large result sets)
- `--sort-by FIELD` - Sorts results by "delay", "departure", "arrival", "airline", or "route"

### seasonal Command Group

Purpose: Historical pattern analysis to identify recurring delay trends

Analysis Performed: Uses historical `/v1/flights` data over 1-3 years to identify recurring delay patterns by month, season, and holiday periods for specific routes, airlines, or airports. Computes month-over-month delay averages, identifies peak delay seasons (like winter storms or summer thunderstorms), and presents seasonal trend charts showing when delays are historically highest/lowest.

### degraded Command Group

Purpose: Performance degradation detection and alerting

Analysis Performed: Compares recent flight performance (last 30-90 days) against historical baselines using rolling window analysis of `/v1/flights` data. Calculates statistical significance of performance changes, detects when current delay rates exceed historical norms by configurable thresholds, and alerts users to airlines/routes showing deteriorating punctuality.

## Technical Architecture

### API Integration

- Primary use of AviationStack `/v1/flights` endpoint for flight data
- Additional endpoints (`/v1/airlines`, `/v1/airports`) for enhanced metadata
- Historical data collection and local storage for trend analysis

### Data Management

- Enhanced SQLite database schema for storing historical flight records
- Shared configuration system across all command groups
- Common data models and error handling infrastructure

### Implementation Approach

1. Phase 1: Extend existing tool to support new command structure and data storage
2. Phase 2: Implement historical data collection capabilities
3. Phase 3: Build seasonal analysis functionality
4. Phase 4: Add performance degradation detection and alerting

## Excluded Features

The following features were considered but excluded from the initial scope:

- `--aircraft-type` filtering (complexity of aircraft data management)
- `--international-only` / `--domestic-only` flags (requires country mapping logic)
- `--live` continuous refresh mode (scope and complexity concerns)

## Learning Objectives

This extension will provide hands-on experience with:

- Advanced CLI design patterns using Typer command groups
- Time-series data analysis with pandas
- Statistical analysis and trend detection
- SQLite database design and optimization
- Historical data management and caching strategies