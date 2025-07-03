package com.antonputra;

import java.util.Set;

import io.smallrye.mutiny.Uni;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/api/devices")
public class DeviceResource {
    private static final Set<Device> devices = Set.of(
        new Device("b0e42fe7-31a5-4894-a441-007e5256afea", "5F-33-CC-1F-43-82", "2.1.6"),
        new Device("0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", "EF-2B-C4-F5-D6-34", "2.1.5"),
        new Device("b16d0b53-14f1-4c11-8e29-b9fcef167c26", "62-46-13-B7-B3-A1", "3.0.0"),
        new Device("51bb1937-e005-4327-a3bd-9f32dcf00db8", "96-A8-DE-5B-77-14", "1.0.1"),
        new Device("e0a1d085-dce5-48db-a794-35640113fa67", "7E-3B-62-A6-09-12", "3.5.6")
    );

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Uni<Set<Device>> list() {
        return Uni.createFrom().item(devices);
    }
}
