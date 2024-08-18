# AFKbot

## Sequence Diagram

<!-- ```mermaid -->
<!-- flowchart TD -->
<!--     SFE[Slack App] --> |1. Slash command trigger| F[FastAPI Server] -->
<!--     F <--> |2. Incoming request authentication| S[Slack API] -->
<!--     F <--> |3. Parsing datetime| L[afk_parser] -->
<!--     F <--> |4. Read/Write DB| D[MongoDB] -->
<!--     F --> |5. Response Message| SFE -->
<!-- ``` -->

```mermaid
sequenceDiagram
    Slack App->>+FastAPI: Slash command
    %% FastAPI->>Slack API: Validate slash command
    %% Slack API-->>FastAPI: Validate slash command
    FastAPI->>afk_parser: Parse AFK datetimes
    afk_parser-->>FastAPI: 
    FastAPI->>MongoDB: Read/Write records
    MongoDB-->>FastAPI: 
    FastAPI-->>Slack App: Slash command response
```

## Appreciations

- [fastapi](https://github.com/fastapi/fastapi)
- [localtunnel](https://github.com/localtunnel/localtunnel)
- [parsedatetime](https://github.com/bear/parsedatetime)
- [pydantic](https://github.com/pydantic/pydantic)
