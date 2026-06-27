# #2: Configure: Portainer-deployable Docker compose files for the BBD webapp

**State:** OPEN
**Author:** dpcunningham
**Created:** 2026-06-26T19:25:12Z

---

Portainer is supposed to have capability to point directly to compose files in repos. 

So we'll go ahead and see if that works.

Our Docker compose files are: [here](https://github.com/vyzed-public/repk8_webapp_buy-borrow-die_sim-calc/tree/main/docker/bbd-calculator)

---

IF we were to deploy in straight Docker, WITHOUT using Portainer, our preference would be:

**Repo structure:**
```
docker/
  bbd-calculator/
    compose.build.yml       # build from source
    compose.deploy.yml      # pull from Docker Hub
```

**On the server (`/var/opt/docker/`):**
```
/var/opt/docker/bbd-calculator/
  compose.build.yml         # copied/pulled from repo
  compose.deploy.yml        # copied/pulled from repo
  compose.yml -> compose.deploy.yml  # symlink to active config
```

**Portainer:** points directly at whichever named file it needs in the repo — no symlink involved.

**CLI on server:** `docker compose up -d` from `/var/opt/docker/bbd-calculator/` follows the symlink transparently.


