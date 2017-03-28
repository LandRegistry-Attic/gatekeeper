Gatekeeper
=====

This service acts as a proxy to the deed-api service.
It has been developed within a Docker container.

See: deed-api at

### Contents

- [Usage](#usage)
- [Available routes](#available-routes)
- [Quick start](#quick-start)
- [tests](#tests)

# Usage

Proxy to the deed-api service.  Accepts and forwards JSON.

# Available routes 

Matches the routes and examples on deed-api.


## Quick start

```shell
export DEED_API_URL=<<Deed API URL>>

./run.sh
```

## tests
```bash
py.test integration_tests
```
or
```bash
py.test unit_tests
```