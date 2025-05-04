package com.antonputra;

import io.smallrye.mutiny.Uni;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/healthz")
public class HealthResource {

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public Uni<String> health() {
        return Uni.createFrom().item("OK");
    }
}
