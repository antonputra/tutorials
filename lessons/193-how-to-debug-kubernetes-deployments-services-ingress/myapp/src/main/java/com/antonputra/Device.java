package com.antonputra;

public class Device {

    public String uuid;
    public String mac;
    public String firmware;

    public Device() {
    }

    public Device(String uuid, String mac, String firmware) {
        this.uuid = uuid;
        this.mac = mac;
        this.firmware = firmware;
    }
}
