# Kubernetes Pod Priority 

[YouTube Tutorial](https://youtu.be/sR_Zmvme3-0)

```bash
kubectl get pods -A
kubectl get pods -A \
    -o jsonpath='{range .items[*]}{.metadata.name}{" - "}{.spec.priorityClassName}{"\n"}{end}'
```
