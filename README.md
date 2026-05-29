# Sentinel: Concurrent Uptime & SSL Monitor

A lightweight, high-performance command-line utility built in Python to monitor website uptime and track SSL certificate health. 

Unlike heavy, agent-based monitoring solutions (like Prometheus or Datadog) or external SaaS APIs, Sentinel relies on **asynchronous I/O** and **raw network sockets** to rapidly verify infrastructure health directly from your terminal.

## The Problem It Solves

As a developer managing multiple personal projects and platforms, keeping track of domain health and SSL expiration dates manually is tedious. I built Sentinel to solve the personal problem of blind spots in my infrastructure. It provides an instant, locally executable snapshot of my web services without the overhead of maintaining a heavy monitoring stack.

## Key Features

* **Blazing Fast Concurrency:** Utilizes Python's `asyncio` and `httpx` to perform non-blocking HTTP requests, allowing dozens of sites to be checked simultaneously in milliseconds.
* **Raw Socket SSL Extraction:** Bypasses third-party APIs by opening secure TCP sockets (`ssl.SSLContext.wrap_socket`) to manually extract and parse X.509 certificate metadata.
* **Graceful Degradation:** Built with resilient error handling to catch DNS lookup failures, connection timeouts, and unexpected network drops without crashing the execution loop.
* **Declarative Configuration:** Uses a strongly typed, easily readable `yaml` file for defining monitoring targets.
* **Rich Terminal UI:** Renders a clean, color-coded dashboard directly in the terminal for immediate visual feedback.

## System Architecture

Sentinel follows a decoupled, modular monolith design tailored for CLI execution:
1. **Configuration Manager:** Parses `targets.yaml` into strict Data Classes to ensure type safety.
2. **Concurrency Engine:** An `asyncio` event loop that manages non-blocking network I/O.
3. **Network Probes (Worker Layer):**
    * *Uptime Probe:* Dispatches asynchronous HTTP `HEAD` requests to minimize bandwidth and server load.
        * *SSL Probe:* Runs blocking raw socket operations inside background threads (`asyncio.to_thread`) to prevent blocking the main event loop.

## Installation & Setup

1. **Clone the repository:**
```bash
git clone [https://github.com/tomi3-11/sentinel-monitor.git](https://github.com/tomi3-11/sentinel-monitor.git)

cd sentinel-monitor
```

2. **Create a virtual environment:**
```bash
# if uv installed
uv venv
source .venv/bin/activate

#python
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install the dependencies:** <br>
Even a better and faster way using uv to sync all the dependencies from the `uv.lock` file.
```bash
# with uv
uv sync
```
OR via pip
```bash
pip install -r requirements.txt
```

4. **Use docker to save the hastle.**
```sh
# make sure docker is up and running
sudo systemctl status docker

# if not
sudo systemctl start docker

# run the program
chmod +x automate # change execution permissions
./automate # run it
```

## Configuration

Create a `targets.yaml` file in the root directory. Add the websites you wish to monitor:

```yaml
settings:
  timeout: 5

  sites:
    - name: "ClubIQ Production"
      url: "[https://clubiq.example.com](https://clubiq.example.com)"
    - name: "Google"
      url: "[https://google.com](https://google.com)"
```

## Usage

Run the monitor from your terminal:

```bash
python monitor/cli.py -c <config-file.yml>
```

### Example Output:

`[*] Loaded 2 sites from targets.yaml...`

| Status | Site Name | URL | HTTP Code | Response Time | SSL Expires |
| :---: | :--- | :--- | :---: | :---: | :---: |
| UP | ClubIQ Production | https://clubiq.example.com | 200 | 142.5ms | 84 days |
| UP | Google | https://google.com | 200 | 89.2ms | 62 days |
