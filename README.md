# Course Scraper

## Setup

1. Install SOPS:
```
brew install sops
```

2. Decrypt the environment file:
```
sops --config ./sops.yaml -d secrets.env > .env
```

3. Fill in the missing values in the `values.env` file.