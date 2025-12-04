FROM mcr.microsoft.com/devcontainers/python:3.12

# Install OS deps
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws/

# Install AWS SAM CLI
RUN curl -Lo sam.zip https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip \
    && unzip sam.zip -d sam-installation \
    && ./sam-installation/install \
    && rm -rf sam.zip sam-installation

# Install Node.js (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Allow VS Code user
USER vscode