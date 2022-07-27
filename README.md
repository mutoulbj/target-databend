# target-databend

`target-databend` is a Singer target for [Databend](https://github.com/datafuselabs/databend).

Build with the [Meltano Target SDK](https://sdk.meltano.com).

## Installation

```bash
pipx install git+https://github.com/mutoulbj/target-databend.git
```

## Configuration

### Accepted Config Options

| Option | Type | Description | Required | Default |
| ------ | ---- | ----------- | -------- | ------- |
| host | string | The hostname of the TargetDatabend server | Yes | localhost |
| port | integer | The port of the TargetDatabend server | Yes | 3307 |
| user | string | The username of the TargetDatabend server | Yes | root |
| password | string | The password of the TargetDatabend server | Yes | |
| dbname | string | The name of the TargetDatabend database | Yes | target_databend |
| charset | string | The character set of the TargetDatabend database | No | utf8 |

A full list of supported settings and capabilities for this
target is available by running:

```bash
target-databend --about
```

### Configure using environment variables

This Singer target will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `target-databend` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Target Directly

```bash
target-databend --version
target-databend --help
# Test using the "Carbon Intensity" sample:
tap-carbon-intensity | target-databend --config /path/to/target-databend-config.json
```

## Developer Resources

- [ ] `Developer TODO:` As a first step, scan the entire project for the text "`TODO:`" and complete any recommended steps, deleting the "TODO" references once completed.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `target_databend/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `target-databend` CLI interface directly using `poetry run`:

```bash
poetry run target-databend --help
```

### Testing with [Meltano](https://meltano.com/)

_**Note:** This target will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd target-databend
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke target-databend --version
# OR run a test `elt` pipeline with the Carbon Intensity sample tap:
meltano elt tap-carbon-intensity target-databend
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the Meltano SDK to
develop your own Singer taps and targets.
