# Helm 3 Dependencies Condition (3 Ways to Add Dependency)

## Option one
```bash
$ helm create app
$ helm create database
```

### Add Dependency to your app chart
```yaml
# app/Chart.yaml

dependencies:
- name: database
  version: 0.1.0
  condition: database.enabled
  repository: file://../database
```

### Add YAML key/value to enable Helm chart
```yaml
# app/values.yaml

database:
  enabled: true
```

### Build Helm dependencies and install chart
```bash
$ helm dependency update
$ helm install -f values.yaml web .
```
---
## Option two
```bash
$ helm create app
$ helm create database
```

### Add Dependency to your app chart
```yaml
# app/Chart.yaml

dependencies:
- name: database
  version: 0.1.0
  enabled: true
  repository: file://../database
```

### Build Helm dependencies and install chart
```bash
$ helm dependency update
$ helm install -f values.yaml web .
```

---
## Option Three
```bash
$ helm create app
$ helm create database
```

### Add Dependency to your app chart
```yaml
# app/Chart.yaml

dependencies:
- name: database
  version: 0.1.0
  repository: file://../database
  tags:
  - database
```

### Add YAML key/value to enable Helm chart
```yaml
# app/values.yaml

tags:
  database: true
```

### Build Helm dependencies and install chart
```bash
$ helm dependency update
$ helm install -f values.yaml web .
```
