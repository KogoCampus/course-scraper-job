module.exports = {
  apps : [{
    name: 'scrape',
    script: './scrapers/main.py',
    autorestart: false,
    interpreter: '.venv/bin/python3',
    cron_restart: "0 0 1,15 * *",
    watch: false,
  }],
};

// pm2 start ecosystem.config.js