# Authentication: Try It Yourself

This is the exercise for my video about authentication. Maya is a DevOps engineer at Harbor, a delivery company. You call Harbor's private Status API with her password, with a reporting job's API key, with an opaque token and with a JWT, and see what the API checks each time.

You need Docker with Compose (start Docker Desktop first, or the Docker service on Linux) and about 600 MB of free disk space.

## 1. Start the exercise

```bash
docker compose up -d --wait
```

The first start downloads about 80 MB (Python and Caddy) and builds the exercise's image (about 450 MB on disk), which takes a minute or less. `init` shows `Exited`: it only makes Harbor Sign-in's signing key, then stops.

Now open a shell inside the toolbox, and run every command in steps 2 to 6 there:

```bash
docker compose exec toolbox bash
```

The prompt starts with `root@`. The toolbox has `curl` and the `harbor` helpers. Nothing is published on your computer: every request goes from this shell to Harbor inside Docker. On Windows, use PowerShell or Windows Terminal; in Git Bash, put `winpty` in front of the command.

## 2. The first private request

Ask for the status of the tracking service without logging in:

```bash
curl -i http://api.harbor.localhost:8080/api/status/tracking
```

You get `401 Unauthorized` and `Www-Authenticate: Basic realm="Harbor"`. The API doesn't know who you are, and it tells you how to log in. Now send Maya's username and password:

```bash
curl -i -u maya:demo-only http://api.harbor.localhost:8080/api/status/tracking
```

You get `200 OK` and `"status":"Healthy"`. The `X-Harbor-Checked` header is this exercise's own: it shows what the API checked, here Maya's password against the hash Harbor stores. A real API doesn't send it.

curl put the username and password into one header. See it:

```bash
curl -sv -u maya:demo-only -o /dev/null http://api.harbor.localhost:8080/api/status/tracking 2>&1 | grep Authorization
echo bWF5YTpkZW1vLW9ubHk= | base64 -d; echo
```

The header is `Authorization: Basic bWF5YTpkZW1vLW9ubHk=`, and it decodes to `maya:demo-only`. Base64 is an encoding, not encryption, so anyone who sees the request can read the password. That's why Basic auth needs HTTPS (here the request never leaves Docker).

Try a wrong password:

```bash
curl -i -u maya:wrong http://api.harbor.localhost:8080/api/status/tracking
```

You get `401` again, with `"reason":"wrong username or password"`.

## 3. The reporting job's own key

A reporting job checks the status every few minutes. It doesn't use Maya's password; it has its own API key:

```bash
harbor job
```

The job sends its key in the `X-API-Key` header and gets `200 OK`. Now the job asks to change a service setting:

```bash
harbor job --change
```

You get `403 Forbidden`. The API knows exactly who is calling, and the answer is still no: the key can only read. A key the API doesn't know gets `401` instead:

```bash
harbor job --key job_demo_madeup
```

`401` means "who are you?", and `403` means "I know who you are, and you can't do that". The key's record shows what it may do:

```bash
harbor key show
```

## 4. Bearer tokens

A Bearer token goes in the `Authorization: Bearer` header, and whoever holds it gets in, so it's handled like a password. The dashboard's backend calls the API with an opaque token, a random string that means nothing on its own:

```bash
curl -i -H "Authorization: Bearer $(harbor token --opaque)" http://api.harbor.localhost:8080/api/status/tracking
```

`X-Harbor-Checked` starts with `opaque token: looked up, active`: the API looked the token up in its own records.

The other kind is a JWT (JSON Web Token), an access token that carries its own information. In the full lab, Harbor Sign-in, the company's sign-in service, gives Maya one after she logs in. Here the helper makes one the same way, signed with Harbor Sign-in's key. Make one and decode it:

```bash
TOKEN=$(harbor token)
harbor jwt decode "$TOKEN"
```

A JWT carries claims, fields that say who and what it's for: who issued it (`"iss"`), whose token it is (`"sub": "maya-01"`), which API it's for (`"aud": "harbor-status-api"`), what it allows (`"scope": "status:read"`), when it was issued (`iat`) and when it expires (`exp`, 5 minutes later). A JWT is signed, not encrypted: anyone holding it can read it. Send it:

```bash
curl -i -H "Authorization: Bearer $TOKEN" http://api.harbor.localhost:8080/api/status/tracking
```

`X-Harbor-Checked` starts with `JWT: signature (key ...), issuer, audience, expiry`. The API checked the token on its own, with Harbor Sign-in's public key, which it fetched from Harbor Sign-in and keeps for 5 minutes. It didn't ask Harbor Sign-in about this token.

The token lasts 5 minutes and is kept only in this shell. If a command below says `the token has expired` or `three parts`, run `TOKEN=$(harbor token)` again.

## 5. Tokens that should fail

Give the token more permissions and keep its old signature:

```bash
BAD=$(harbor jwt edit "$TOKEN" scope="status:read settings:write")
curl -i -X PUT -H "Authorization: Bearer $BAD" http://api.harbor.localhost:8080/api/settings/tracking
```

`401` and `the signature doesn't match the token's content`. Changing one claim breaks the signature. Next, a token made for another API:

```bash
curl -i -H "Authorization: Bearer $(harbor token --other-api)" http://api.harbor.localhost:8080/api/status/tracking
```

`the token was made for harbor-billing-api, not for harbor-status-api`. The signature is fine, but the audience is wrong. And a token that expired 5 minutes ago:

```bash
curl -i -H "Authorization: Bearer $(harbor token --expired)" http://api.harbor.localhost:8080/api/status/tracking
```

`the token has expired`.

## 6. Optional: rotate the job's key

```bash
harbor key rotate
harbor job
harbor job --key job_demo_4Kx9Qe2mVt7Lp1Zr8Ws3
```

The job now sends its new key and gets `200`. The old key gets `401` and `this API key was revoked`. That's how you replace a leaked key without touching Maya's password.

## 7. Clean up

Type `exit` to leave the toolbox, then:

```bash
docker compose down -v
```

To delete the exercise's images as well, run `docker compose down -v --rmi all` instead.

## The full lab

The full lab has all nine missions, about 40 minutes: Maya's browser login and its session cookie, a request from another website, logout, the partner app that connects with OAuth 2.0 and PKCE, Sign in with Harbor, and retiring the job's key. Its files are in the [lab](lab) folder next to this README, and its steps are on https://antonputra.com/labs/authentication/
