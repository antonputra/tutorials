package com.antonputra;

import java.util.UUID;
import java.time.LocalDateTime;

public record Image(UUID imageId, LocalDateTime createdAt, String objKey) {

    public Image(String objKey) {
        this(UUID.randomUUID(), LocalDateTime.now(), objKey);
    }
}
