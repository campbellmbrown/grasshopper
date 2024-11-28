# StaSSH

StaSSH is a "stash" of your SSH connections.
The goal is to provide a simple GUI allowing easily connections to your servers without having to remember tedious commands.

> [!NOTE]
> Only Windows is supported for now.

## Direct Connections

Direct connections are the most simple way to connect to a server. They have the following properties:

- **Host**: The IP address or domain name of the server.
- **Port**: The port used for the connection.
- **User**: The username used for authentication.
- **Key**: The private key used for authentication.

These additional properties are for personal identification:

- **Name**
- **Note**

Direct connections are saved to `%APPDATA%/StaSSH/direct_connections.json` on Windows and `~/.config/StaSSH/connections.json` on Linux.

# Setup

## Install Requirements

```bash
pip install -r requirements.txt
```

# Run

## From the Command Line

```bash
python run.py
```

## From VS Code

You can also run the application from VS Code by running the `StaSSH` configuration.
