const crypto = require("crypto");

const signingSecret = "0726fa5c951306c31fbe0c329d2ce736";
const baseString = "v0:1626992929:{\"token\":\"UdG3UFNsPGoobvRzK5F2oIqe\",\"challenge\":\"6KaNtlamllYYaLZ7qhHxZbzyYut62TlDKu2wAZXp4rZlInRbcDTH\",\"type\":\"url_verification\"}";

const hmac = crypto.createHmac("sha256", signingSecret)
    .update(baseString)
    .digest("hex");

console.log(hmac)
