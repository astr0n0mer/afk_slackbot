# AFKbot

## Request Flow

```mermaid
flowchart TD
    SFE[Slack App] --> |1. Slash command trigger| F[FastAPI Server]
    F <--> |2. POST Request authentication| S[Slack API]
    F <--> |3. Parsing datetime| L[afk_parser]
    F <--> |4. Read/Write DB| D[MongoDB]
```

## Appreciations

- [fastapi](https://github.com/fastapi/fastapi)
- [localtunnel](https://github.com/localtunnel/localtunnel)
- [parsedatetime](https://github.com/bear/parsedatetime)
- [pydantic](https://github.com/pydantic/pydantic)
