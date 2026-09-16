# LoopDesk

LoopDesk is a Python agent runtime with MCP-native tools, durable sessions,
local memory, multi-channel messaging, and a local web control UI.

The package is published as part of an LoopDesk release zip. Install from the
release bundle rather than from a source checkout so the wheel, dependency
wheelhouse, install scripts, and third-party notices stay together.

## Requirements

- Python 3.12 or newer.
- A configured model provider for live model calls.
- Optional channel credentials only for the channel integrations you enable.

## After Install

Run the onboarding command before starting the gateway:

```sh
loopdesk onboard --if-needed
```

Then start the local gateway:

```sh
loopdesk gateway run
```

## Project Links

Repository, license, release, and third-party notice information are included in
the release bundle and in the public LoopDesk repository.
