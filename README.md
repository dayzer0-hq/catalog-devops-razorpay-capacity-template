# Razorpay settlement worker — requests and limits you can defend

Two modes, and they use very different amounts of memory:

| `MODE` | what it does |
|---|---|
| `steady` | three cycles, allocating `BATCH_MB/8` each |
| `eod` | the end-of-day batch: allocates `BATCH_MB` at once and holds it for 30 seconds |

`BATCH_MB` defaults to 64. The allocation is real, so a memory limit below it actually kills
the pod — which is the point.

## How to reproduce the end-of-day batch

    docker build -t settlement:0.1.0 .
    docker run --rm -e MODE=eod -e BATCH_MB=256 settlement:0.1.0

To watch it be killed by a limit:

    docker run --rm -m 128m -e MODE=eod -e BATCH_MB=256 settlement:0.1.0
    # exits 137 — OOMKilled

## How to observe a pod's actual usage

`kubectl top` needs metrics-server, which `kind` does not install by default:

    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    kubectl patch deployment metrics-server -n kube-system --type=json \
      -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
    kubectl top pod -l app=settlement

⚠️ Without that patch metrics-server will not start on kind, and `kubectl top` reports an error
that reads like your pod is broken rather than like the metrics pipeline is missing.

## What is in `k8s/deployment.yaml`

Requests and limits **copied from another service**. Nobody measured this worker. Replacing
them with defensible numbers is your work, and the two failure modes — throttled on CPU, killed
on memory — want describing separately because they feel completely different in production.
