## How to run the application locally?

### Navigate to the '0-app' directory

```bash
cd tutorials/lessons/182/0-app
```

### Download the application's dependencies

```bash
go mod tidy
```

### Run the application

```bash
go run .
```

### Access the application from a separate terminal window

```bash
curl -i localhost:8080/api/devices
```

### Get the current status of the application.

```bash
curl -i localhost:8080/status
```