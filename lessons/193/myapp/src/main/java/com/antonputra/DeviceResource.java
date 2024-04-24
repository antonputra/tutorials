package com.antonputra;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Set;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/api/devices")
public class DeviceResource {

    private Set<Device> devices = Collections.newSetFromMap(Collections.synchronizedMap(new LinkedHashMap<>()));

    public DeviceResource() {
        devices.add(new Device("b0e42fe7-31a5-4894-a441-007e5256afea", "5F-33-CC-1F-43-82", "2.1.6"));
        devices.add(new Device("0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", "EF-2B-C4-F5-D6-34", "2.1.5"));
    }

    @GET
    public Set<Device> list() {
        return devices;
    }
}
