<!-- Dashboard chrome: header and stat panels are static SVGs in img/ -->
<img src="img/header.svg" alt="Josh Strebeck · DevOps Supervisor" width="100%">

<img src="img/stats-row.svg" alt="Role: DevOps Supervisor · 9 years in IT · 7 AWS certifications · CKA · 4 homelab nodes · 19 Argo CD apps" width="100%">

<p align="center">
  <a href="https://github.com/jstrebeck/Homelab-Configuration/actions/workflows/validate.yaml"><img src="https://img.shields.io/github/actions/workflow/status/jstrebeck/Homelab-Configuration/validate.yaml?branch=main&style=flat-square&label=homelab%20validate&labelColor=181b1f" alt="Homelab validate"></a>
  <a href="https://github.com/jstrebeck/Homelab-Configuration/commits/main"><img src="https://img.shields.io/github/last-commit/jstrebeck/Homelab-Configuration?style=flat-square&label=homelab%20last%20sync&labelColor=181b1f&color=73bf69" alt="Homelab last commit"></a>
  <a href="https://github.com/jstrebeck/payments-fraud-detection/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/jstrebeck/payments-fraud-detection/ci.yml?branch=main&style=flat-square&label=fraud%20detection%20ci&labelColor=181b1f" alt="payments-fraud-detection CI"></a>
  <a href="https://github.com/jstrebeck/strebeck.net/actions/workflows/hugo.yaml"><img src="https://img.shields.io/github/actions/workflow/status/jstrebeck/strebeck.net/hugo.yaml?branch=main&style=flat-square&label=strebeck.net%20deploy&labelColor=181b1f" alt="strebeck.net deploy"></a>
  <a href="https://github.com/jstrebeck/jstrebeck/actions/workflows/reconcile.yaml"><img src="https://img.shields.io/github/actions/workflow/status/jstrebeck/jstrebeck/reconcile.yaml?branch=main&style=flat-square&label=this%20readme%20reconcile&labelColor=181b1f" alt="README reconcile"></a>
</p>

## About

DevOps Supervisor at a PCI DSS-regulated payments company, nine years in IT. I led the migration of a monolithic payments platform to microservices on Amazon EKS, cutting AWS costs 12%, built a Backstage developer platform that put deployments in every engineer's hands, and operate ML fraud detection on SageMaker. At home I run a four-node bare-metal Kubernetes cluster that is managed entirely through Git, and most of the projects below are built on top of it.

**Hands-on with:** Kubernetes, Argo CD, Terraform, AWS, Talos Linux, Rook-Ceph, Prometheus and Grafana, MLflow, KServe, Kubeflow, and self-hosted LLM inference.

**Certified:** AWS Solutions Architect Professional · AWS DevOps Engineer Professional · AWS Machine Learning Engineer Associate · AWS Advanced Networking Specialty · CKA · Terraform Associate

**Find me:** [strebeck.net](https://strebeck.net) · [LinkedIn](https://www.linkedin.com/in/jstrebeck) · [josh@strebeck.net](mailto:josh@strebeck.net)

## Activity

<img src="img/contributions.svg" alt="GitHub contribution heatmap for the last 12 months" width="100%">

<p align="center"><img src="https://streak-stats.demolab.com?user=jstrebeck&background=181b1f&border=2c3235&ring=ff780a&fire=ff780a&currStreakNum=ffffff&sideNums=ffffff&currStreakLabel=ccccdc&sideLabels=ccccdc&dates=9fa7b3&stroke=2c3235" alt="Contribution streak"></p>

## Delivery

Featured repositories, presented the way Argo CD lists applications. Project, source path and destination are declared in [`apps.json`](apps.json). Health, revision, language, stars and last sync are rendered daily from the GitHub API by [`scripts/reconcile.py`](scripts/reconcile.py), so a failing CI run on any of them turns its row Degraded.

<a href="https://github.com/jstrebeck/Homelab-Configuration"><img src="img/apps/homelab-configuration.svg" alt="Homelab-Configuration: Healthy, Synced" width="100%"></a>
<a href="https://github.com/jstrebeck/payments-fraud-detection"><img src="img/apps/payments-fraud-detection.svg" alt="payments-fraud-detection: Healthy, Synced" width="100%"></a>
<a href="https://github.com/jstrebeck/game-server-platform"><img src="img/apps/game-server-platform.svg" alt="game-server-platform: Healthy, Synced" width="100%"></a>
<a href="https://github.com/jstrebeck/demand-forecast-mlops"><img src="img/apps/demand-forecast-mlops.svg" alt="demand-forecast-mlops: Healthy, Synced" width="100%"></a>
<a href="https://github.com/jstrebeck/strebflow"><img src="img/apps/strebflow.svg" alt="strebflow: Healthy, Synced" width="100%"></a>
<a href="https://github.com/jstrebeck/strebeck.net"><img src="img/apps/strebeck-net.svg" alt="strebeck.net: Healthy, Synced" width="100%"></a>
<a href="https://github.com/jstrebeck/Dotfiles"><img src="img/apps/dotfiles.svg" alt="Dotfiles: Healthy, Synced" width="100%"></a>

## Application tree

The homelab runs Argo CD's app-of-apps pattern. One root Application, applied once by hand, owns every platform component and every workload. This is that tree, the same way Argo CD draws it, with the repos each application syncs from.

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontFamily": "Inter, -apple-system, Segoe UI, Roboto, sans-serif", "primaryColor": "#262626", "primaryBorderColor": "#3a3a3a", "primaryTextColor": "#e6e6e6", "lineColor": "#8fa4b1", "clusterBkg": "#1c1c1c", "clusterBorder": "#3a3a3a", "edgeLabelBackground": "#1c1c1c"}}}%%
flowchart LR
  ROOT["root<br/>app of apps · Healthy · Synced<br/>jstrebeck/Homelab-Configuration"]
  subgraph platform["AppProject: platform  ·  source: Homelab-Configuration"]
    direction TB
    ARGO["argocd"]
    METAL["metallb"]
    CEPH["rook-ceph"]
    MON["kube-prometheus-stack"]
    CM["cert-manager"]
    KS["kserve"]
    SW["seaweedfs"]
    ML["mlflow"]
    REG["registry"]
    CF["cloudflared"]
  end
  subgraph workloads["AppProjects: workloads  ·  source: their own repos"]
    direction TB
    PFD["payments-fraud-detection<br/>deploy/overlays/homelab"]
    GSP["game-server-platform<br/>deployment/"]
    DF["demand-forecast-mlops<br/>pipelines/"]
    SF["strebflow<br/>k8s/"]
  end
  subgraph off["Outside the cluster"]
    direction TB
    WEB["strebeck.net<br/>Hugo on GitHub Pages"]
    CRP["Cloud-Resume-Project<br/>AWS, built by a self-hosted runner on the lab"]
  end
  ROOT --> ARGO
  ROOT --> METAL
  ROOT --> CEPH
  ROOT --> MON
  ROOT --> CM
  ROOT --> KS
  ROOT --> SW
  ROOT --> ML
  ROOT --> REG
  ROOT --> CF
  ROOT --> PFD
  ROOT --> GSP
  ROOT --> DF
  ROOT --> SF
  KS -. serves the champion model .-> PFD
  ML -. tracking and registry .-> DF
  METAL -. LoadBalancer IPs .-> GSP
  ROOT -. write-ups .-> WEB
  ROOT -. Actions runner VM .-> CRP
  classDef root fill:#1b2e27,stroke:#18be94,color:#ffffff
  classDef plat fill:#262626,stroke:#3a3a3a,color:#e6e6e6
  classDef work fill:#262626,stroke:#7fb3ff,color:#e6e6e6
  classDef ext fill:#1c1c1c,stroke:#3a3a3a,color:#8fa4b1
  class ROOT root
  class ARGO,METAL,CEPH,MON,CM,KS,SW,ML,REG,CF plat
  class PFD,GSP,DF,SF work
  class WEB,CRP ext
```

## Linux desktop

I do all of my work from a Linux desktop and keep the whole environment in Git so a fresh machine is familiar in about half an hour.

<table>
  <tr>
    <td width="60%"><a href="https://github.com/jstrebeck/Dotfiles"><img src="img/desktop.jpg" alt="Sway desktop with Alacritty terminals and Waybar" width="100%"></a></td>
    <td width="40%" valign="top">
      <b><a href="https://github.com/jstrebeck/Dotfiles">Dotfiles</a></b><br>
      Sway on Wayland, Waybar, Rofi, Alacritty, Mako and zsh, managed with GNU Stow. One <code>deps.sh</code> bootstraps a Debian-based install, and a branch per machine carries hardware-specific config. <a href="https://strebeck.net/posts/dotfiles-a-reproducible-sway-desktop-with-gnu-stow/">Write-up</a>
      <br><br>
      <b><a href="https://github.com/jstrebeck/neovim-config">neovim-config</a></b><br>
      Neovim is my editor for everything. Built on the NvChad starter, large enough to live in its own repo, and cloned by the dotfiles setup script.
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="50%"><img src="img/js80.jpg" alt="JS80 keyboard case rendered in Fusion 360" width="100%"></td>
    <td width="50%"><img src="img/jsergo.jpg" alt="JSErgo split keyboard, finished build" width="100%"></td>
  </tr>
  <tr>
    <td colspan="2">
      <b>Custom keyboards.</b> The JS80 and the split JSErgo are handwired builds with cases designed in Fusion 360 and firmware in my <a href="https://github.com/jstrebeck/qmk_firmware/tree/6f7dd71c28859d08f4661c501d80a9a2bc3899c0/keyboards/handwired/jstrebeck">QMK fork</a>. <a href="https://strebeck.net/posts/custom-keyboard-builds-js80-and-jsergo/">Write-up</a>
    </td>
  </tr>
</table>

## Latest posts

From [strebeck.net](https://strebeck.net/posts/), refreshed daily by a GitHub Action from the site's RSS feed.

<!-- BLOG-POST-LIST:START -->
- May 08, 2026 · [Dotfiles: A Reproducible Sway Desktop With GNU Stow](https://strebeck.net/posts/dotfiles-a-reproducible-sway-desktop-with-gnu-stow/)
- Apr 04, 2026 · [Training and Monitoring ML Models With PyTorch, MLflow, and Kubeflow](https://strebeck.net/posts/training-and-monitoring-ml-models-with-pytorch-mlflow-and-kubeflow/)
- Mar 29, 2026 · [StrebFlow: An Autonomous Coding Pipeline Built on LangGraph](https://strebeck.net/posts/strebflow-an-autonomous-coding-pipeline-built-on-langgraph/)
- Jan 25, 2026 · [Game Server Platform: Multi-Tenant Minecraft Hosting on Kubernetes](https://strebeck.net/posts/game-server-platform-multi-tenant-minecraft-hosting-on-kubernetes/)
- Jan 18, 2026 · [Homelab Configuration: GitOps on Talos Kubernetes with Argo CD](https://strebeck.net/posts/homelab-configuration-terraform-ansible-and-kubernetes-on-proxmox/)
- Oct 12, 2024 · [Fastest way to create a homelab Kubernetes cluster](https://strebeck.net/posts/homelab-kubernetes-cluster/)<!-- BLOG-POST-LIST:END -->

<sub>Dashboard defined in Git. Header and stat panels are static SVGs, the streak panel comes from streak-stats, and the contribution heatmap, application rows and posts are reconciled daily by GitHub Actions.</sub>
