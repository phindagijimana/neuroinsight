# Troubleshooting Mac - Containers Exiting

## Run these commands on your Mac and share the output:

```bash
# 1. Check if you have the latest changes
cd ~/Downloads/neuroinsight-web-app
git log --oneline -5

# 2. Check if platform flag is in docker-compose.yml
grep -A 2 "worker:" docker-compose.yml

# 3. Check container status
docker-compose ps

# 4. Check logs for errors
docker-compose logs backend | tail -50
docker-compose logs worker | tail -50

# 5. Check if platform flag is actually being used
docker-compose config | grep -A 5 "worker:"
```

Share the output of all these commands so I can see what's wrong.


