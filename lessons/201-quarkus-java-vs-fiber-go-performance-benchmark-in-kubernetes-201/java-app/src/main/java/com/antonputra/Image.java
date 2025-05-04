package com.antonputra;

import java.util.UUID;
import java.time.LocalDateTime;

public class Image {

    public UUID imageId;
    public LocalDateTime createdAt;
    public String objKey;

    public Image(String objKey) {
        this.imageId = UUID.randomUUID();
        this.createdAt = LocalDateTime.now();
        this.objKey = objKey;
    }
}
